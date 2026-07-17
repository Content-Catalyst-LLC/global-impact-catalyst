#!/usr/bin/env python3
"""Command-line workspace, repository, and evidence operations for v1.3.0."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from python.global_impact_repository import SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService


def read_json(path:str): return json.loads(Path(path).read_text(encoding='utf-8'))
def emit(value): print(json.dumps(value,indent=2,ensure_ascii=False,default=lambda o:o.__dict__))

def main()->int:
    parser=argparse.ArgumentParser(description='Global Impact Catalyst persistent repository and evidence CLI')
    parser.add_argument('--database',default='outputs/global-impact-catalyst.sqlite3')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('init')
    create=sub.add_parser('create'); create.add_argument('--input',required=True); create.add_argument('--generated-at'); create.add_argument('--allow-invalid',action='store_true')
    imp=sub.add_parser('import'); imp.add_argument('--input',required=True); imp.add_argument('--generated-at')
    listing=sub.add_parser('list'); listing.add_argument('--workspace-id'); listing.add_argument('--search',default=''); listing.add_argument('--status'); listing.add_argument('--include-archived',action='store_true')
    show=sub.add_parser('show'); show.add_argument('--initiative-id',required=True)
    duplicate=sub.add_parser('duplicate'); duplicate.add_argument('--initiative-id',required=True); duplicate.add_argument('--name',required=True); duplicate.add_argument('--workspace-name'); duplicate.add_argument('--generated-at')
    archive=sub.add_parser('archive'); archive.add_argument('--initiative-id',required=True); archive.add_argument('--revision',required=True,type=int)
    restore=sub.add_parser('restore'); restore.add_argument('--initiative-id',required=True); restore.add_argument('--revision',required=True,type=int)
    export=sub.add_parser('export'); export.add_argument('--workspace-id',required=True); export.add_argument('--output',required=True)
    restore_bundle=sub.add_parser('restore-bundle'); restore_bundle.add_argument('--input',required=True)
    backup=sub.add_parser('backup'); backup.add_argument('--output',required=True)
    sources=sub.add_parser('sources'); sources.add_argument('--workspace-id'); sources.add_argument('--initiative-id'); sources.add_argument('--search',default='')
    add_source=sub.add_parser('add-source'); add_source.add_argument('--input',required=True); add_source.add_argument('--workspace-id',required=True); add_source.add_argument('--initiative-id'); add_source.add_argument('--expected-revision',type=int)
    version=sub.add_parser('add-source-version'); version.add_argument('--source-id',required=True); version.add_argument('--file',required=True); version.add_argument('--label',default=''); version.add_argument('--mime-type',default='application/octet-stream'); version.add_argument('--captured-by',default='cli')
    evidence=sub.add_parser('capture-evidence'); evidence.add_argument('--source-id',required=True); evidence.add_argument('--input',required=True)
    dataset=sub.add_parser('register-dataset'); dataset.add_argument('--source-id',required=True); dataset.add_argument('--input',required=True)
    link=sub.add_parser('link-evidence'); link.add_argument('--claim-id',required=True); link.add_argument('--evidence-id',required=True); link.add_argument('--relationship',default='supports'); link.add_argument('--strength',default='direct'); link.add_argument('--notes',default='')
    chain=sub.add_parser('evidence-chain'); chain.add_argument('--initiative-id',required=True); chain.add_argument('--output')
    sub.add_parser('summary')
    args=parser.parse_args()
    with SQLiteImpactRepository(args.database) as repository:
        service=ImpactApplicationService(repository)
        if args.command=='init': emit({'database':args.database,'schema_version':repository.schema_version,'migrations':repository.applied_migrations()})
        elif args.command=='create': emit(service.create_initiative(read_json(args.input),generated_at=args.generated_at,allow_invalid=args.allow_invalid))
        elif args.command=='import': emit(service.import_document(read_json(args.input),generated_at=args.generated_at).__dict__)
        elif args.command=='list': emit(service.list_initiatives(workspace_id=args.workspace_id,search=args.search,lifecycle_status=args.status,include_archived=args.include_archived))
        elif args.command=='show': emit(repository.get_contract(initiative_id=args.initiative_id))
        elif args.command=='duplicate': emit(service.duplicate_initiative(args.initiative_id,new_name=args.name,target_workspace_name=args.workspace_name,generated_at=args.generated_at))
        elif args.command=='archive': emit(repository.archive_entity('initiative',args.initiative_id,expected_revision=args.revision))
        elif args.command=='restore': emit(repository.restore_entity('initiative',args.initiative_id,expected_revision=args.revision))
        elif args.command=='export': emit({'output':str(Path(args.output)),'bundle':service.export_workspace(args.workspace_id,args.output)})
        elif args.command=='restore-bundle': emit(service.restore_workspace(read_json(args.input)))
        elif args.command=='backup': emit({'backup':str(repository.backup_database(args.output))})
        elif args.command=='sources': emit(repository.list_sources(workspace_id=args.workspace_id,initiative_id=args.initiative_id,search=args.search))
        elif args.command=='add-source': emit(service.register_source(read_json(args.input),workspace_id=args.workspace_id,initiative_id=args.initiative_id,expected_revision=args.expected_revision,actor='cli'))
        elif args.command=='add-source-version':
            path=Path(args.file); emit(service.add_source_version(args.source_id,version_label=args.label,payload=path.read_bytes(),mime_type=args.mime_type,size_bytes=path.stat().st_size,captured_by=args.captured_by,metadata={'filename':path.name}))
        elif args.command=='capture-evidence': emit(service.capture_evidence(args.source_id,**read_json(args.input)))
        elif args.command=='register-dataset': emit(service.register_dataset(args.source_id,read_json(args.input),actor='cli'))
        elif args.command=='link-evidence': emit(service.link_claim_evidence(args.claim_id,args.evidence_id,relationship=args.relationship,strength=args.strength,notes=args.notes,linked_by='cli'))
        elif args.command=='evidence-chain': emit(service.evidence_chain(args.initiative_id,args.output))
        elif args.command=='summary': emit(repository.repository_summary())
    return 0
if __name__=='__main__': raise SystemExit(main())
