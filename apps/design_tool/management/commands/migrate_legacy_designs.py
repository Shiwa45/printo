"""
Management command to migrate legacy single-sided designs to new format
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.design_tool.models import UserDesign, DesignTemplate
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate legacy single-sided designs to new front/back format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of designs to process in each batch',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting legacy design migration (dry_run={dry_run})'
            )
        )
        
        # Find designs that need migration
        legacy_designs = UserDesign.objects.filter(
            design_type__isnull=True  # Old designs don't have design_type set
        ).exclude(
            design_data__isnull=True
        )
        
        total_count = legacy_designs.count()
        self.stdout.write(f'Found {total_count} legacy designs to migrate')
        
        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No legacy designs found. Migration complete.')
            )
            return
        
        migrated_count = 0
        error_count = 0
        
        # Process in batches
        for i in range(0, total_count, batch_size):
            batch = legacy_designs[i:i + batch_size]
            
            self.stdout.write(f'Processing batch {i//batch_size + 1}...')
            
            with transaction.atomic():
                for design in batch:
                    try:
                        if self.migrate_design(design, dry_run):
                            migrated_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        logger.error(f'Error migrating design {design.id}: {e}')
                        error_count += 1
        
        # Report results
        self.stdout.write(
            self.style.SUCCESS(
                f'Migration complete: {migrated_count} migrated, {error_count} errors'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    'This was a dry run. No changes were made. '
                    'Run without --dry-run to apply changes.'
                )
            )

    def migrate_design(self, design, dry_run=False):
        """Migrate a single design from legacy format to new format"""
        try:
            # Check if design already has new format
            if design.design_type:
                self.stdout.write(f'Design {design.id} already migrated, skipping')
                return True
            
            # Validate that we have legacy data to migrate
            if not design.design_data:
                self.stdout.write(f'Design {design.id} has no legacy data, skipping')
                return False
            
            if dry_run:
                self.stdout.write(
                    f'Would migrate design {design.id} ({design.name}) to single-sided format'
                )
                return True
            
            # Migrate to new format
            design.design_type = 'single'
            # Keep existing design_data as-is for backward compatibility
            # Don't set front_design_data or back_design_data for single-sided designs
            
            design.save(update_fields=['design_type'])
            
            self.stdout.write(
                f'Migrated design {design.id} ({design.name}) to single-sided format'
            )
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Failed to migrate design {design.id}: {e}'
                )
            )
            return False

    def validate_migration(self):
        """Validate that migration was successful"""
        # Check for any designs without design_type
        unmigrated = UserDesign.objects.filter(design_type__isnull=True).count()
        
        if unmigrated > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'{unmigrated} designs still need migration'
                )
            )
            return False
        
        # Check for designs with invalid design_type
        invalid_types = UserDesign.objects.exclude(
            design_type__in=['single', 'front_only', 'back_only', 'both_sides']
        ).count()
        
        if invalid_types > 0:
            self.stdout.write(
                self.style.ERROR(
                    f'{invalid_types} designs have invalid design_type'
                )
            )
            return False
        
        self.stdout.write(
            self.style.SUCCESS('Migration validation passed')
        )
        return True