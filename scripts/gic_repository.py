#!/usr/bin/env python3
"""Command-line workspace and repository operations for v1.2.0."""
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
    parser=argparse.ArgumentParser(description='Global Impact Catalyst persistent repository CLI')
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
        elif args.command=='summary': emit(repository.repository_summary())
    return 0
if __name__=='__main__': raise SystemExit(main())
