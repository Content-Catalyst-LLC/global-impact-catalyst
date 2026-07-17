"""Governed reporting, publication snapshots, dashboards, and reproducible exports.

Global Impact Catalyst v1.8.0 turns governed repository state into accessible
reports and deterministic export bundles. Generated outputs are descriptive
artifacts, not assurance, certification, audit findings, or causal proof.
"""
from __future__ import annotations

import hashlib
import html
import io
import json
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

REPORTING_VERSION = "1.8.0"
REPORT_TYPES = {"impact_report", "public_brief", "methodology_report", "portfolio_report", "board_report"}
CITATION_STYLES = {"harvard", "apa", "plain"}
CARD_TYPES = {"metric", "trend", "target", "evidence", "quality", "budget", "scenario", "narrative"}
DEFAULT_SECTIONS = ["executive_summary", "initiative", "results", "evidence", "analysis", "quality", "methodology", "limitations", "references"]

class ReportingError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(data: Any) -> str:
    raw = data if isinstance(data, (bytes, bytearray)) else _canonical(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _id(kind: str, *parts: Any) -> str:
    return f"gic-{kind}-{hashlib.sha256('|'.join(str(x) for x in parts).encode()).hexdigest()[:20]}"


def _json(row: Any, field: str) -> Any:
    return json.loads(row[field]) if row[field] else {}


def _citation(source: Dict[str, Any], style: str) -> Dict[str, Any]:
    creator = source.get("creator") or "Unknown author"
    year = str(source.get("published_at") or "n.d.")[:4]
    title = source.get("title") or "Untitled source"
    publisher = source.get("publisher") or ""
    locator = source.get("doi") or source.get("url") or source.get("locator") or ""
    if style == "apa":
        formatted = f"{creator}. ({year}). {title}. {publisher}. {locator}".replace(". .", ".").strip()
    elif style == "plain":
        formatted = " — ".join(part for part in [creator, title, year, locator] if part)
    else:
        formatted = f"{creator} ({year}) {title}. {publisher}. {locator}".replace(". .", ".").strip()
    return {"source_id": source["source_id"], "creator": creator, "year": year, "title": title,
            "publisher": publisher, "locator": locator, "formatted": formatted}


class ReportingPublicationMixin:
    @contextmanager
    def _reporting_transaction(self) -> Iterator[Any]:
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            yield self.connection
        except Exception:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    @staticmethod
    def _decode_report(row: Any) -> Dict[str, Any]:
        item = dict(row)
        for field in ("document_json", "citations_json", "methodology_json", "metadata_json"):
            item[field[:-5] if field.endswith("_json") else field] = json.loads(item.pop(field))
        return item

    def register_report_template(self, template: Dict[str, Any], *, workspace_id: str,
                                 expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        name = str(template.get("name") or "").strip()
        if not name:
            raise ReportingError("report template requires name")
        report_type = str(template.get("report_type") or "impact_report")
        if report_type not in REPORT_TYPES:
            raise ReportingError(f"unsupported report type: {report_type}")
        citation_style = str(template.get("citation_style") or "harvard")
        if citation_style not in CITATION_STYLES:
            raise ReportingError(f"unsupported citation style: {citation_style}")
        template_id = str(template.get("template_id") or _id("report-template", workspace_id, name))
        existing = self.connection.execute("SELECT revision,created_at FROM report_templates WHERE template_id=?", (template_id,)).fetchone()
        now = _now(); revision = 1
        if existing:
            actual = int(existing["revision"])
            if expected_revision is not None and expected_revision != actual:
                self._registry_concurrency("report_template", template_id, expected_revision, actual)
            revision = actual + 1; created_at = existing["created_at"]
        else:
            if expected_revision not in (None, 0):
                self._registry_concurrency("report_template", template_id, expected_revision, 0)
            created_at = now
        values = (template_id, workspace_id, name, str(template.get("description") or ""), report_type,
                  _canonical(template.get("sections") or DEFAULT_SECTIONS), citation_style,
                  _canonical(template.get("accessibility_profile") or {"wcag_target":"2.2 AA","heading_order":True,"table_captions":True,"text_alternatives":True}),
                  str(template.get("lifecycle_status") or "draft"), revision, created_at, now,
                  _canonical(template.get("metadata") or {}))
        with self._reporting_transaction():
            self.connection.execute("""INSERT OR REPLACE INTO report_templates(template_id,workspace_id,name,description,report_type,sections_json,citation_style,accessibility_profile_json,lifecycle_status,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", values)
            self._audit("upsert", "report_template", template_id, workspace_id=workspace_id, revision=revision, actor=actor)
        return self.get_report_template(template_id)

    def get_report_template(self, template_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM report_templates WHERE template_id=?", (template_id,)).fetchone()
        if not row: raise ReportingError(f"report template not found: {template_id}")
        item = dict(row)
        item["sections"] = json.loads(item.pop("sections_json")); item["accessibility_profile"] = json.loads(item.pop("accessibility_profile_json")); item["metadata"] = json.loads(item.pop("metadata_json"))
        return item

    def list_report_templates(self, workspace_id: str) -> List[Dict[str, Any]]:
        return [self.get_report_template(row["template_id"]) for row in self.connection.execute("SELECT template_id FROM report_templates WHERE workspace_id=? ORDER BY name", (workspace_id,))]

    def _report_sources(self, workspace_id: str, initiative_id: str, style: str) -> List[Dict[str, Any]]:
        sources = self.list_sources(workspace_id=workspace_id, initiative_id=initiative_id)
        return [_citation(source, style) for source in sources]

    def _report_context(self, workspace_id: str, initiative_id: str) -> Dict[str, Any]:
        contract = self.get_contract(initiative_id=initiative_id)
        return {"contract": contract, "evidence": self.evidence_chain(initiative_id),
                "registry": self.export_indicator_registry(workspace_id),
                "measurement": self.export_measurement_repository(workspace_id),
                "review": self.export_review_workflow(workspace_id),
                "analysis": self.export_analysis_repository(workspace_id)}

    def _compose_report(self, *, title: str, report_type: str, audience: str, period_label: str,
                        language: str, sections: List[str], context: Dict[str, Any], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        contract = context["contract"]["contract"]; facts = contract["facts"]; derived = contract.get("derived") or {}
        initiative = facts["initiative"]; goal = facts["goal"]; outcomes = facts.get("outcomes") or []
        measurement = facts["measurement"]; observation = (measurement.get("observations") or [{}])[-1]
        metrics = derived.get("metrics") or {}; interpretation = derived.get("interpretation") or {}
        quality = context["review"].get("integrity") or {}; analysis_integrity = context["analysis"].get("integrity") or {}
        methodology = {
            "canonical_contract_version": contract.get("contract_version"),
            "evidence_repository_version": context["evidence"].get("chain_version"),
            "indicator_registry_version": context["registry"].get("registry_version"),
            "measurement_repository_version": context["measurement"].get("repository_version"),
            "review_workflow_version": context["review"].get("workflow_version"),
            "analysis_repository_version": context["analysis"].get("repository_version"),
            "source_count": len(citations), "method_count": len(facts.get("methods") or []),
            "calculation_provenance": contract.get("calculation_provenance") or {},
            "boundary": contract.get("boundary") or "",
        }
        content = {
            "report_type": report_type, "title": title, "audience": audience, "language": language,
            "period_label": period_label, "initiative": {"id": initiative["id"], "name": initiative["name"]},
            "executive_summary": interpretation.get("summary") or f"{initiative['name']} reports governed impact evidence for {period_label or 'the selected period'}.",
            "goal": goal.get("statement", ""), "outcomes": outcomes,
            "indicator": {"name": facts["indicator"].get("name"), "unit": observation.get("unit"),
                          "observed_value": observation.get("value"), "period": observation.get("period"),
                          "baseline": measurement.get("baseline"), "target": measurement.get("target")},
            "metrics": metrics, "interpretation": interpretation,
            "evidence_summary": context["evidence"].get("integrity") or {},
            "analysis_summary": analysis_integrity, "quality_summary": quality,
            "methodology": methodology,
            "limitations": list(dict.fromkeys([*(m.get("limitations") or [] for m in [])])) if False else [
                "Validation tests consistency and traceability, not truth or source authenticity.",
                "Observed change does not by itself establish attribution or causality.",
                "Scenario and trend outputs are descriptive or planning artifacts, not verified forecasts."
            ],
            "citations": citations,
            "sections": sections,
        }
        return content

    @staticmethod
    def _render_markdown(document: Dict[str, Any]) -> str:
        indicator = document["indicator"]; lines = [f"# {document['title']}", "", f"**Audience:** {document['audience']}", f"**Reporting period:** {document['period_label'] or 'Not specified'}", ""]
        if "executive_summary" in document["sections"]: lines += ["## Executive summary", document["executive_summary"], ""]
        if "initiative" in document["sections"]: lines += ["## Initiative and goal", f"**{document['initiative']['name']}**", "", document["goal"], ""]
        if "results" in document["sections"]: lines += ["## Results", f"- Indicator: {indicator['name']}", f"- Observed value: {indicator['observed_value']} {indicator['unit']}", f"- Period: {(indicator.get('period') or {}).get('label','')}", ""]
        if "analysis" in document["sections"]: lines += ["## Analysis", f"- Saved analysis runs: {document['analysis_summary'].get('analysis_run_count',0)}", f"- Scenarios: {document['analysis_summary'].get('scenario_count',0)}", ""]
        if "quality" in document["sections"]: lines += ["## Review and quality", f"- Review workflow valid: {document['quality_summary'].get('valid',False)}", f"- Publications: {document['quality_summary'].get('publication_count',0)}", ""]
        if "methodology" in document["sections"]: lines += ["## Methodology appendix", *[f"- {k.replace('_',' ').title()}: {v}" for k,v in document["methodology"].items()], ""]
        if "limitations" in document["sections"]: lines += ["## Limitations", *[f"- {x}" for x in document["limitations"]], ""]
        if "references" in document["sections"]: lines += ["## References", *[f"{i+1}. {c['formatted']}" for i,c in enumerate(document["citations"])], ""]
        return "\n".join(lines).rstrip()+"\n"

    @staticmethod
    def _render_html(document: Dict[str, Any]) -> str:
        esc = html.escape; indicator=document["indicator"]
        sections=[]
        sections.append(f'<section aria-labelledby="summary"><h2 id="summary">Executive summary</h2><p>{esc(str(document["executive_summary"]))}</p></section>')
        sections.append(f'<section aria-labelledby="results"><h2 id="results">Results</h2><dl><dt>Indicator</dt><dd>{esc(str(indicator["name"]))}</dd><dt>Observed value</dt><dd>{esc(str(indicator["observed_value"]))} {esc(str(indicator["unit"]))}</dd><dt>Period</dt><dd>{esc(str((indicator.get("period") or {}).get("label","")))}</dd></dl></section>')
        sections.append('<section aria-labelledby="limitations"><h2 id="limitations">Limitations</h2><ul>'+''.join(f'<li>{esc(x)}</li>' for x in document["limitations"])+"</ul></section>")
        sections.append('<section aria-labelledby="references"><h2 id="references">References</h2><ol>'+''.join(f'<li id="ref-{i+1}">{esc(c["formatted"])}</li>' for i,c in enumerate(document["citations"]))+"</ol></section>")
        return '<!doctype html><html lang="'+esc(document["language"])+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(document["title"])+'</title></head><body><a href="#main">Skip to report</a><main id="main"><header><h1>'+esc(document["title"])+f'</h1><p>Audience: {esc(document["audience"])}</p></header>'+''.join(sections)+'</main></body></html>\n'

    def create_report(self, report: Dict[str, Any], *, workspace_id: str, initiative_id: str,
                      template_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        template = self.get_report_template(template_id) if template_id else None
        report_type = str(report.get("report_type") or (template or {}).get("report_type") or "impact_report")
        if report_type not in REPORT_TYPES: raise ReportingError(f"unsupported report type: {report_type}")
        title = str(report.get("title") or "Impact Report").strip(); audience=str(report.get("audience") or "public")
        language=str(report.get("language") or "en"); period_label=str(report.get("period_label") or "")
        sections=list(report.get("sections") or (template or {}).get("sections") or DEFAULT_SECTIONS)
        citation_style=str(report.get("citation_style") or (template or {}).get("citation_style") or "harvard")
        context=self._report_context(workspace_id, initiative_id); citations=self._report_sources(workspace_id, initiative_id, citation_style)
        source_bundle={key:_hash(value) for key,value in context.items()}; source_bundle_hash=_hash(source_bundle)
        document=self._compose_report(title=title, report_type=report_type, audience=audience, period_label=period_label,
                                      language=language, sections=sections, context=context, citations=citations)
        markdown=self._render_markdown(document); rendered_html=self._render_html(document); document_hash=_hash(document)
        report_id=str(report.get("report_id") or _id("report", workspace_id, initiative_id, title, source_bundle_hash))
        now=_now(); existing=self.connection.execute("SELECT revision,created_at FROM report_documents WHERE report_id=?",(report_id,)).fetchone()
        revision=int(existing["revision"])+1 if existing else 1; created_at=existing["created_at"] if existing else now
        with self._reporting_transaction():
            self.connection.execute("""INSERT OR REPLACE INTO report_documents(report_id,workspace_id,initiative_id,template_id,title,report_type,audience,language,period_label,lifecycle_status,source_bundle_hash,content_hash,document_json,rendered_markdown,rendered_html,citations_json,methodology_json,revision,created_by,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (report_id,workspace_id,initiative_id,template_id,title,report_type,audience,language,period_label,str(report.get("lifecycle_status") or "draft"),source_bundle_hash,document_hash,_canonical(document),markdown,rendered_html,_canonical(citations),_canonical(document["methodology"]),revision,actor,created_at,now,_canonical({**(report.get("metadata") or {}),"source_hashes":source_bundle})))
            self._audit("generate", "report", report_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor, details={"content_hash":document_hash})
        return self.get_report(report_id)

    def get_report(self, report_id: str) -> Dict[str, Any]:
        row=self.connection.execute("SELECT * FROM report_documents WHERE report_id=?",(report_id,)).fetchone()
        if not row: raise ReportingError(f"report not found: {report_id}")
        return self._decode_report(row)

    def list_reports(self, *, workspace_id: Optional[str]=None, initiative_id: Optional[str]=None) -> List[Dict[str, Any]]:
        sql="SELECT report_id FROM report_documents WHERE 1=1"; args=[]
        if workspace_id: sql+=" AND workspace_id=?"; args.append(workspace_id)
        if initiative_id: sql+=" AND initiative_id=?"; args.append(initiative_id)
        sql+=" ORDER BY updated_at DESC"
        return [self.get_report(row["report_id"]) for row in self.connection.execute(sql,args)]

    def create_dashboard(self, dashboard: Dict[str, Any], *, workspace_id: str, initiative_id: Optional[str]=None,
                         expected_revision: Optional[int]=None, actor: str="system") -> Dict[str, Any]:
        name=str(dashboard.get("name") or "").strip()
        if not name: raise ReportingError("dashboard requires name")
        dashboard_id=str(dashboard.get("dashboard_id") or _id("dashboard",workspace_id,initiative_id or "workspace",name))
        existing=self.connection.execute("SELECT revision,created_at FROM dashboard_definitions WHERE dashboard_id=?",(dashboard_id,)).fetchone(); now=_now()
        if existing and expected_revision is not None and expected_revision!=int(existing["revision"]): self._registry_concurrency("dashboard",dashboard_id,expected_revision,int(existing["revision"]))
        revision=int(existing["revision"])+1 if existing else 1; created_at=existing["created_at"] if existing else now
        with self._reporting_transaction():
            self.connection.execute("""INSERT OR REPLACE INTO dashboard_definitions(dashboard_id,workspace_id,initiative_id,name,description,audience,layout_json,lifecycle_status,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (dashboard_id,workspace_id,initiative_id,name,str(dashboard.get("description") or ""),str(dashboard.get("audience") or "internal"),_canonical(dashboard.get("layout") or {"columns":2}),str(dashboard.get("lifecycle_status") or "draft"),revision,created_at,now,_canonical(dashboard.get("metadata") or {})))
            self._audit("upsert","dashboard",dashboard_id,workspace_id=workspace_id,initiative_id=initiative_id,revision=revision,actor=actor)
        return self.get_dashboard(dashboard_id)

    def add_dashboard_card(self, dashboard_id: str, card: Dict[str, Any], *, actor: str="system") -> Dict[str, Any]:
        dashboard=self.get_dashboard(dashboard_id); card_type=str(card.get("card_type") or "narrative")
        if card_type not in CARD_TYPES: raise ReportingError(f"unsupported dashboard card type: {card_type}")
        title=str(card.get("title") or "").strip()
        if not title: raise ReportingError("dashboard card requires title")
        card_id=str(card.get("card_id") or _id("dashboard-card",dashboard_id,title,card_type))
        with self._reporting_transaction():
            self.connection.execute("""INSERT OR REPLACE INTO dashboard_cards(card_id,dashboard_id,card_type,title,subject_type,subject_id,position,alt_text,configuration_json,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (card_id,dashboard_id,card_type,title,str(card.get("subject_type") or ""),str(card.get("subject_id") or ""),int(card.get("position") or 0),str(card.get("alt_text") or title),_canonical(card.get("configuration") or {}),_canonical(card.get("metadata") or {})))
            self._audit("add_card","dashboard",dashboard_id,workspace_id=dashboard["workspace_id"],initiative_id=dashboard.get("initiative_id"),actor=actor,details={"card_id":card_id})
        return next(x for x in self.get_dashboard(dashboard_id)["cards"] if x["card_id"]==card_id)

    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        row=self.connection.execute("SELECT * FROM dashboard_definitions WHERE dashboard_id=?",(dashboard_id,)).fetchone()
        if not row: raise ReportingError(f"dashboard not found: {dashboard_id}")
        item=dict(row); item["layout"]=json.loads(item.pop("layout_json")); item["metadata"]=json.loads(item.pop("metadata_json"))
        cards=[]
        for c in self.connection.execute("SELECT * FROM dashboard_cards WHERE dashboard_id=? ORDER BY position,title",(dashboard_id,)):
            card=dict(c); card["configuration"]=json.loads(card.pop("configuration_json")); card["metadata"]=json.loads(card.pop("metadata_json")); cards.append(card)
        item["cards"]=cards; return item

    def render_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        dashboard=self.get_dashboard(dashboard_id); cards=[]
        for card in dashboard["cards"]:
            value=None
            cfg=card["configuration"]
            if card["card_type"]=="metric": value=cfg.get("value")
            elif card["card_type"]=="quality": value=self.export_review_workflow(dashboard["workspace_id"])["integrity"]
            elif card["card_type"]=="evidence": value=self.export_evidence_repository(dashboard["workspace_id"])["integrity"]
            elif card["card_type"]=="trend" and card["subject_id"]:
                run=self.get_analysis_run(card["subject_id"]); value=run.get("result")
            else: value=cfg.get("text") or cfg
            cards.append({**card,"value":value})
        return {"dashboard_type":"global_impact_dashboard","dashboard_version":REPORTING_VERSION,"dashboard_id":dashboard_id,
                "workspace_id":dashboard["workspace_id"],"initiative_id":dashboard.get("initiative_id"),"name":dashboard["name"],
                "audience":dashboard["audience"],"layout":dashboard["layout"],"cards":cards,
                "accessibility":{"card_count":len(cards),"all_cards_have_alt_text":all(bool(x["alt_text"]) for x in cards)},
                "boundary":"Dashboard summaries inherit the limitations of their governed source records."}

    def create_publication_snapshot(self, publication_id: str, *, report_id: Optional[str]=None, actor: str="system") -> Dict[str, Any]:
        publication=self.get_publication(publication_id)
        if publication["publication_status"]!="published": raise ReportingError("publication snapshot requires a published publication")
        workspace_id=publication["workspace_id"]; initiative_id=publication["initiative_id"]
        contract=self.get_contract(initiative_id=initiative_id); evidence=self.export_evidence_repository(workspace_id)
        registry=self.export_indicator_registry(workspace_id); measurement=self.export_measurement_repository(workspace_id)
        review=self.export_review_workflow(workspace_id); analysis=self.export_analysis_repository(workspace_id)
        report=self.get_report(report_id) if report_id else None
        hashes={"contract_hash":_hash(contract),"evidence_hash":_hash(evidence),"registry_hash":_hash(registry),"measurement_hash":_hash(measurement),"review_hash":_hash(review),"analysis_hash":_hash(analysis),"report_hash":report["content_hash"] if report else ""}
        snapshot={"snapshot_type":"global_impact_publication_snapshot","snapshot_version":REPORTING_VERSION,"publication":publication,"report":report,"hashes":hashes}
        snapshot_hash=_hash(snapshot); snapshot_id=_id("publication-snapshot",publication_id,snapshot_hash); now=_now()
        with self._reporting_transaction():
            self.connection.execute("""INSERT OR IGNORE INTO publication_snapshots(snapshot_id,publication_id,workspace_id,initiative_id,report_id,release_label,snapshot_hash,contract_hash,evidence_hash,registry_hash,measurement_hash,review_hash,analysis_hash,report_hash,snapshot_json,created_by,created_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (snapshot_id,publication_id,workspace_id,initiative_id,report_id,publication.get("release_label") or "",snapshot_hash,hashes["contract_hash"],hashes["evidence_hash"],hashes["registry_hash"],hashes["measurement_hash"],hashes["review_hash"],hashes["analysis_hash"],hashes["report_hash"],_canonical(snapshot),actor,now,"{}"))
            self._audit("snapshot","publication",publication_id,workspace_id=workspace_id,initiative_id=initiative_id,actor=actor,details={"snapshot_id":snapshot_id,"snapshot_hash":snapshot_hash})
        return self.get_publication_snapshot(snapshot_id)

    def get_publication_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        row=self.connection.execute("SELECT * FROM publication_snapshots WHERE snapshot_id=?",(snapshot_id,)).fetchone()
        if not row: raise ReportingError(f"publication snapshot not found: {snapshot_id}")
        item=dict(row); item["snapshot"]=json.loads(item.pop("snapshot_json")); item["metadata"]=json.loads(item.pop("metadata_json")); return item

    @staticmethod
    def _zip_bytes(artifacts: Dict[str, str]) -> bytes:
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,"w",zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(artifacts):
                info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
                zf.writestr(info,artifacts[path].encode("utf-8"))
        return buffer.getvalue()

    def build_reproducible_export(self, *, workspace_id: str, initiative_id: Optional[str]=None,
                                  report_id: Optional[str]=None, publication_snapshot_id: Optional[str]=None,
                                  destination: Optional[str|Path]=None, actor: str="system") -> Dict[str, Any]:
        report=self.get_report(report_id) if report_id else None
        snapshot=self.get_publication_snapshot(publication_snapshot_id) if publication_snapshot_id else None
        workspace=self.export_workspace_bundle(workspace_id)
        def normalize_export(value: Any) -> Any:
            if isinstance(value, dict):
                normalized = {}
                for key, item in value.items():
                    if key in {"generated_at", "exported_at"}:
                        normalized[key] = "1980-01-01T00:00:00+00:00"
                    elif key == "audit":
                        normalized[key] = []
                    elif key == "export_bundles" and value.get("repository_type") == "global_impact_reporting_repository":
                        normalized[key] = []
                    elif key == "export_bundle_count" and "report_count" in value:
                        normalized[key] = 0
                    else:
                        normalized[key] = normalize_export(item)
                return normalized
            if isinstance(value, list):
                return [normalize_export(item) for item in value]
            return value
        workspace = normalize_export(workspace)
        artifacts={"workspace-bundle.json":json.dumps(workspace,indent=2,ensure_ascii=False)+"\n"}
        if report:
            artifacts.update({"report/report.json":json.dumps(report["document"],indent=2,ensure_ascii=False)+"\n","report/report.md":report["rendered_markdown"],"report/report.html":report["rendered_html"],"report/citations.json":json.dumps(report["citations"],indent=2,ensure_ascii=False)+"\n","report/methodology.json":json.dumps(report["methodology"],indent=2,ensure_ascii=False)+"\n"})
        if snapshot: artifacts["publication-snapshot.json"]=json.dumps(snapshot["snapshot"],indent=2,ensure_ascii=False)+"\n"
        checksums={path:hashlib.sha256(content.encode()).hexdigest() for path,content in artifacts.items()}
        manifest={"bundle_type":"global_impact_reproducible_export","bundle_version":REPORTING_VERSION,"workspace_id":workspace_id,"initiative_id":initiative_id,"report_id":report_id,"publication_snapshot_id":publication_snapshot_id,"artifacts":[{"path":p,"media_type":"text/html" if p.endswith(".html") else "text/markdown" if p.endswith(".md") else "application/json","byte_size":len(artifacts[p].encode()),"sha256":checksums[p]} for p in sorted(artifacts)],"reproducibility":{"deterministic_zip_timestamps":True,"hash_algorithm":"sha256"},"boundary":"Export integrity proves byte identity, not factual truth, assurance, or causal validity."}
        manifest_text=json.dumps(manifest,indent=2,ensure_ascii=False)+"\n"; artifacts["manifest.json"]=manifest_text
        artifacts["SHA256SUMS.txt"]="".join(f"{hashlib.sha256(artifacts[p].encode()).hexdigest()}  {p}\n" for p in sorted(artifacts))
        archive=self._zip_bytes(artifacts); manifest_hash=_hash(manifest); archive_hash=hashlib.sha256(archive).hexdigest(); export_bundle_id=_id("export-bundle",workspace_id,manifest_hash)
        now=_now()
        with self._reporting_transaction():
            self.connection.execute("""INSERT OR REPLACE INTO export_bundles(export_bundle_id,workspace_id,initiative_id,report_id,publication_snapshot_id,bundle_version,status,manifest_hash,archive_hash,artifact_count,created_by,created_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (export_bundle_id,workspace_id,initiative_id,report_id,publication_snapshot_id,REPORTING_VERSION,"complete",manifest_hash,archive_hash,len(artifacts),actor,now,"{}"))
            self.connection.execute("DELETE FROM export_artifacts WHERE export_bundle_id=?",(export_bundle_id,))
            for path,content in artifacts.items():
                self.connection.execute("""INSERT INTO export_artifacts(artifact_id,export_bundle_id,artifact_path,media_type,byte_size,sha256,content_text,created_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?)""",
                (_id("export-artifact",export_bundle_id,path),export_bundle_id,path,"text/html" if path.endswith(".html") else "text/markdown" if path.endswith(".md") else "text/plain" if path.endswith(".txt") else "application/json",len(content.encode()),hashlib.sha256(content.encode()).hexdigest(),content,now,"{}"))
            self._audit("build","export_bundle",export_bundle_id,workspace_id=workspace_id,initiative_id=initiative_id,actor=actor,details={"archive_hash":archive_hash})
        output_path=None
        if destination:
            output_path=Path(destination); output_path.parent.mkdir(parents=True,exist_ok=True); output_path.write_bytes(archive)
        return {"export_bundle_id":export_bundle_id,"bundle_version":REPORTING_VERSION,"workspace_id":workspace_id,"initiative_id":initiative_id,"manifest":manifest,"manifest_hash":manifest_hash,"archive_hash":archive_hash,"artifact_count":len(artifacts),"path":str(output_path) if output_path else None,"archive_bytes":archive}

    @staticmethod
    def verify_reproducible_export(path: str|Path) -> Dict[str, Any]:
        archive=Path(path).read_bytes(); failures=[]
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            names=set(zf.namelist()); manifest=json.loads(zf.read("manifest.json"));
            for item in manifest["artifacts"]:
                if item["path"] not in names: failures.append(f"missing:{item['path']}"); continue
                actual=hashlib.sha256(zf.read(item["path"])).hexdigest()
                if actual!=item["sha256"]: failures.append(f"checksum:{item['path']}")
        return {"valid":not failures,"failures":failures,"archive_hash":hashlib.sha256(archive).hexdigest(),"manifest":manifest}

    def export_reporting_repository(self, workspace_id: str) -> Dict[str, Any]:
        templates = self.list_report_templates(workspace_id)
        reports = self.list_reports(workspace_id=workspace_id)
        dashboards = [
            self.get_dashboard(row["dashboard_id"])
            for row in self.connection.execute(
                "SELECT dashboard_id FROM dashboard_definitions WHERE workspace_id=? ORDER BY name",
                (workspace_id,),
            )
        ]
        snapshots = [
            self.get_publication_snapshot(row["snapshot_id"])
            for row in self.connection.execute(
                "SELECT snapshot_id FROM publication_snapshots WHERE workspace_id=? ORDER BY created_at",
                (workspace_id,),
            )
        ]

        bundles: List[Dict[str, Any]] = []
        artifact_checksum_failures: List[str] = []
        artifact_size_failures: List[str] = []
        bundle_count_failures: List[str] = []
        bundle_manifest_failures: List[str] = []
        bundle_archive_failures: List[str] = []
        for row in self.connection.execute(
            "SELECT * FROM export_bundles WHERE workspace_id=? ORDER BY created_at",
            (workspace_id,),
        ):
            item = dict(row)
            item["metadata"] = json.loads(item.pop("metadata_json"))
            artifacts: List[Dict[str, Any]] = []
            archive_artifacts: Dict[str, str] = {}
            for artifact_row in self.connection.execute(
                "SELECT * FROM export_artifacts WHERE export_bundle_id=? ORDER BY artifact_path",
                (item["export_bundle_id"],),
            ):
                artifact = dict(artifact_row)
                artifact["metadata"] = json.loads(artifact.pop("metadata_json"))
                content = artifact["content_text"]
                actual_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                actual_size = len(content.encode("utf-8"))
                if actual_hash != artifact["sha256"]:
                    artifact_checksum_failures.append(artifact["artifact_id"])
                if actual_size != int(artifact["byte_size"]):
                    artifact_size_failures.append(artifact["artifact_id"])
                archive_artifacts[artifact["artifact_path"]] = content
                artifacts.append(artifact)
            item["artifacts"] = artifacts
            if len(artifacts) != int(item["artifact_count"]):
                bundle_count_failures.append(item["export_bundle_id"])
            manifest_artifact = next((a for a in artifacts if a["artifact_path"] == "manifest.json"), None)
            if manifest_artifact is None:
                bundle_manifest_failures.append(item["export_bundle_id"])
            else:
                try:
                    manifest = json.loads(manifest_artifact["content_text"])
                    if _hash(manifest) != item["manifest_hash"]:
                        bundle_manifest_failures.append(item["export_bundle_id"])
                except (TypeError, ValueError, json.JSONDecodeError):
                    bundle_manifest_failures.append(item["export_bundle_id"])
            if archive_artifacts:
                rebuilt_hash = hashlib.sha256(self._zip_bytes(archive_artifacts)).hexdigest()
                if rebuilt_hash != item["archive_hash"]:
                    bundle_archive_failures.append(item["export_bundle_id"])
            bundles.append(item)

        report_hash_failures = [
            report["report_id"]
            for report in reports
            if report["content_hash"] != _hash(report["document"])
        ]
        snapshot_hash_failures = [
            snapshot["snapshot_id"]
            for snapshot in snapshots
            if snapshot["snapshot_hash"] != _hash(snapshot["snapshot"])
        ]
        valid = not any(
            (
                report_hash_failures,
                snapshot_hash_failures,
                artifact_checksum_failures,
                artifact_size_failures,
                bundle_count_failures,
                bundle_manifest_failures,
                bundle_archive_failures,
            )
        )
        return {
            "repository_type": "global_impact_reporting_repository",
            "repository_version": REPORTING_VERSION,
            "workspace_id": workspace_id,
            "generated_at": _now(),
            "report_templates": templates,
            "reports": reports,
            "dashboards": dashboards,
            "publication_snapshots": snapshots,
            "export_bundles": bundles,
            "integrity": {
                "valid": valid,
                "template_count": len(templates),
                "report_count": len(reports),
                "dashboard_count": len(dashboards),
                "publication_snapshot_count": len(snapshots),
                "export_bundle_count": len(bundles),
                "report_hash_failures": report_hash_failures,
                "snapshot_hash_failures": snapshot_hash_failures,
                "artifact_checksum_failures": artifact_checksum_failures,
                "artifact_size_failures": artifact_size_failures,
                "bundle_count_failures": bundle_count_failures,
                "bundle_manifest_failures": bundle_manifest_failures,
                "bundle_archive_failures": bundle_archive_failures,
            },
            "boundary": "Reporting and export integrity do not constitute assurance, certification, audit, or causal proof.",
        }

    def _restore_reporting_repository(self, repository: Dict[str, Any], *, actor: str = "restore") -> None:
        if not repository:
            return
        workspace_id = repository["workspace_id"]
        self.connection.commit()
        with self._reporting_transaction():
            for template in repository.get("report_templates", []):
                self.connection.execute(
                    """INSERT OR REPLACE INTO report_templates(
                    template_id,workspace_id,name,description,report_type,sections_json,citation_style,
                    accessibility_profile_json,lifecycle_status,revision,created_at,updated_at,metadata_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        template["template_id"], template["workspace_id"], template["name"],
                        template.get("description") or "", template.get("report_type") or "impact_report",
                        _canonical(template.get("sections") or DEFAULT_SECTIONS),
                        template.get("citation_style") or "harvard",
                        _canonical(template.get("accessibility_profile") or {}),
                        template.get("lifecycle_status") or "draft", int(template.get("revision") or 1),
                        template["created_at"], template["updated_at"],
                        _canonical(template.get("metadata") or {}),
                    ),
                )
            for report in repository.get("reports", []):
                self.connection.execute(
                    """INSERT OR REPLACE INTO report_documents(
                    report_id,workspace_id,initiative_id,template_id,title,report_type,audience,language,
                    period_label,lifecycle_status,source_bundle_hash,content_hash,document_json,
                    rendered_markdown,rendered_html,citations_json,methodology_json,revision,created_by,
                    created_at,updated_at,metadata_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        report["report_id"], report["workspace_id"], report["initiative_id"],
                        report.get("template_id"), report["title"], report["report_type"],
                        report.get("audience") or "public", report.get("language") or "en",
                        report.get("period_label") or "", report.get("lifecycle_status") or "draft",
                        report["source_bundle_hash"], report["content_hash"],
                        _canonical(report["document"]), report["rendered_markdown"], report["rendered_html"],
                        _canonical(report.get("citations") or []), _canonical(report.get("methodology") or {}),
                        int(report.get("revision") or 1), report.get("created_by") or actor,
                        report["created_at"], report["updated_at"], _canonical(report.get("metadata") or {}),
                    ),
                )
            for dashboard in repository.get("dashboards", []):
                self.connection.execute(
                    """INSERT OR REPLACE INTO dashboard_definitions(
                    dashboard_id,workspace_id,initiative_id,name,description,audience,layout_json,
                    lifecycle_status,revision,created_at,updated_at,metadata_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        dashboard["dashboard_id"], dashboard["workspace_id"], dashboard.get("initiative_id"),
                        dashboard["name"], dashboard.get("description") or "",
                        dashboard.get("audience") or "internal", _canonical(dashboard.get("layout") or {}),
                        dashboard.get("lifecycle_status") or "draft", int(dashboard.get("revision") or 1),
                        dashboard["created_at"], dashboard["updated_at"],
                        _canonical(dashboard.get("metadata") or {}),
                    ),
                )
                self.connection.execute("DELETE FROM dashboard_cards WHERE dashboard_id=?", (dashboard["dashboard_id"],))
                for card in dashboard.get("cards", []):
                    self.connection.execute(
                        """INSERT INTO dashboard_cards(
                        card_id,dashboard_id,card_type,title,subject_type,subject_id,position,alt_text,
                        configuration_json,metadata_json
                        ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (
                            card["card_id"], dashboard["dashboard_id"], card["card_type"], card["title"],
                            card.get("subject_type") or "", card.get("subject_id") or "",
                            int(card.get("position") or 0), card.get("alt_text") or card["title"],
                            _canonical(card.get("configuration") or {}), _canonical(card.get("metadata") or {}),
                        ),
                    )
            for snapshot in repository.get("publication_snapshots", []):
                self.connection.execute(
                    """INSERT OR REPLACE INTO publication_snapshots(
                    snapshot_id,publication_id,workspace_id,initiative_id,report_id,release_label,
                    snapshot_hash,contract_hash,evidence_hash,registry_hash,measurement_hash,review_hash,
                    analysis_hash,report_hash,snapshot_json,created_by,created_at,metadata_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        snapshot["snapshot_id"], snapshot["publication_id"], snapshot["workspace_id"],
                        snapshot["initiative_id"], snapshot.get("report_id"), snapshot.get("release_label") or "",
                        snapshot["snapshot_hash"], snapshot["contract_hash"], snapshot["evidence_hash"],
                        snapshot["registry_hash"], snapshot["measurement_hash"], snapshot["review_hash"],
                        snapshot["analysis_hash"], snapshot.get("report_hash") or "",
                        _canonical(snapshot.get("snapshot") or {}), snapshot.get("created_by") or actor,
                        snapshot["created_at"], _canonical(snapshot.get("metadata") or {}),
                    ),
                )
            for bundle in repository.get("export_bundles", []):
                self.connection.execute(
                    """INSERT OR REPLACE INTO export_bundles(
                    export_bundle_id,workspace_id,initiative_id,report_id,publication_snapshot_id,
                    bundle_version,status,manifest_hash,archive_hash,artifact_count,created_by,created_at,metadata_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        bundle["export_bundle_id"], bundle["workspace_id"], bundle.get("initiative_id"),
                        bundle.get("report_id"), bundle.get("publication_snapshot_id"),
                        bundle.get("bundle_version") or REPORTING_VERSION, bundle.get("status") or "complete",
                        bundle["manifest_hash"], bundle.get("archive_hash") or "",
                        int(bundle.get("artifact_count") or len(bundle.get("artifacts") or [])),
                        bundle.get("created_by") or actor, bundle["created_at"],
                        _canonical(bundle.get("metadata") or {}),
                    ),
                )
                self.connection.execute("DELETE FROM export_artifacts WHERE export_bundle_id=?", (bundle["export_bundle_id"],))
                for artifact in bundle.get("artifacts", []):
                    content = artifact.get("content_text") or ""
                    self.connection.execute(
                        """INSERT INTO export_artifacts(
                        artifact_id,export_bundle_id,artifact_path,media_type,byte_size,sha256,
                        content_text,created_at,metadata_json
                        ) VALUES (?,?,?,?,?,?,?,?,?)""",
                        (
                            artifact["artifact_id"], bundle["export_bundle_id"], artifact["artifact_path"],
                            artifact["media_type"], int(artifact.get("byte_size") or len(content.encode("utf-8"))),
                            artifact["sha256"], content, artifact["created_at"],
                            _canonical(artifact.get("metadata") or {}),
                        ),
                    )
            self._audit(
                "restore", "reporting_repository", workspace_id, workspace_id=workspace_id,
                actor=actor, details={"repository_version": repository.get("repository_version")},
            )

