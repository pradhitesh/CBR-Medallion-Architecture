"""add_shared_constraints

Revision ID: 579a2f2a6a26
Revises: 579a2f2a6a26
Create Date: 2026-06-08 14:20:28.008630

Run after both vocab CSVs (0002) and local_concept CSV (0003) are loaded.
Adds PKs first (validated against now-populated data), then indexes, then
intra-shared FKs, and finally the local_concept.concept_id → shared.concept FK.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '579a2f2a6a26'
down_revision: Union[str, Sequence[str], None] = '371d5bcbabe6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Primary Keys
    op.create_primary_key('pk_concept', 'concept', ['concept_id'], schema='shared')
    op.create_primary_key('pk_concept_class', 'concept_class', ['concept_class_id'], schema='shared')
    op.create_primary_key('pk_domain', 'domain', ['domain_id'], schema='shared')
    op.create_primary_key('pk_vocabulary', 'vocabulary', ['vocabulary_id'], schema='shared')
    op.create_primary_key('pk_relationship', 'relationship', ['relationship_id'], schema='shared')

    # 2. Indexes
    op.create_index('idx_concept_class_id', 'concept', ['concept_class_id'], schema='shared')
    op.create_index('idx_concept_code', 'concept', ['concept_code'], schema='shared')
    op.create_index('idx_concept_concept_id', 'concept', ['concept_id'], schema='shared')
    op.create_index('idx_concept_domain_id', 'concept', ['domain_id'], schema='shared')
    op.create_index('idx_concept_vocabluary_id', 'concept', ['vocabulary_id'], schema='shared')

    op.create_index('idx_concept_class_class_id', 'concept_class', ['concept_class_id'], schema='shared')
    op.create_index('idx_domain_domain_id', 'domain', ['domain_id'], schema='shared')
    op.create_index('idx_vocabulary_vocabulary_id', 'vocabulary', ['vocabulary_id'], schema='shared')
    op.create_index('idx_relationship_rel_id', 'relationship', ['relationship_id'], schema='shared')

    op.create_index('idx_concept_ancestor_id_1', 'concept_ancestor', ['ancestor_concept_id'], schema='shared')
    op.create_index('idx_concept_ancestor_id_2', 'concept_ancestor', ['descendant_concept_id'], schema='shared')
    
    op.create_index('idx_concept_synonym_id', 'concept_synonym', ['concept_id'], schema='shared')
    
    op.create_index('idx_drug_strength_id_1', 'drug_strength', ['drug_concept_id'], schema='shared')
    op.create_index('idx_drug_strength_id_2', 'drug_strength', ['ingredient_concept_id'], schema='shared')
    
    op.create_index('idx_concept_relationship_id_1', 'concept_relationship', ['concept_id_1'], schema='shared')
    op.create_index('idx_concept_relationship_id_2', 'concept_relationship', ['concept_id_2'], schema='shared')
    op.create_index('idx_concept_relationship_id_3', 'concept_relationship', ['relationship_id'], schema='shared')

    # 3. Foreign Keys
    # Concept
    op.create_foreign_key('fk_concept_concept_class', 'concept', 'concept_class', ['concept_class_id'], ['concept_class_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_concept_domain', 'concept', 'domain', ['domain_id'], ['domain_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_concept_vocabulary', 'concept', 'vocabulary', ['vocabulary_id'], ['vocabulary_id'], source_schema='shared', referent_schema='shared')
    
    # Concept Class
    op.create_foreign_key('fk_concept_class_concept', 'concept_class', 'concept', ['concept_class_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    
    # Domain
    op.create_foreign_key('fk_domain_concept', 'domain', 'concept', ['domain_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    
    # Vocabulary
    op.create_foreign_key('fk_vocabulary_concept', 'vocabulary', 'concept', ['vocabulary_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    
    # Relationship
    op.create_foreign_key('fk_relationship_concept', 'relationship', 'concept', ['relationship_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    
    # Concept Ancestor
    op.create_foreign_key('fk_ca_ancestor', 'concept_ancestor', 'concept', ['ancestor_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_ca_descendant', 'concept_ancestor', 'concept', ['descendant_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    
    # Concept Synonym
    op.create_foreign_key('fk_cs_concept', 'concept_synonym', 'concept', ['concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_cs_language', 'concept_synonym', 'concept', ['language_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    
    # Drug Strength
    op.create_foreign_key('fk_ds_drug', 'drug_strength', 'concept', ['drug_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_ds_ingredient', 'drug_strength', 'concept', ['ingredient_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_ds_amount_unit', 'drug_strength', 'concept', ['amount_unit_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_ds_numerator_unit', 'drug_strength', 'concept', ['numerator_unit_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_ds_denominator_unit', 'drug_strength', 'concept', ['denominator_unit_concept_id'], ['concept_id'], source_schema='shared', referent_schema='shared')
    
    # Concept Relationship
    op.create_foreign_key('fk_cr_concept_1', 'concept_relationship', 'concept', ['concept_id_1'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_cr_concept_2', 'concept_relationship', 'concept', ['concept_id_2'], ['concept_id'], source_schema='shared', referent_schema='shared')
    op.create_foreign_key('fk_cr_relationship', 'concept_relationship', 'relationship', ['relationship_id'], ['relationship_id'], source_schema='shared', referent_schema='shared')

    # NOTE: local_concept.concept_id is intentionally NOT a foreign key to
    # shared.concept. The values in local_concept are CBR-assigned custom
    # concept IDs (2,000,000,000+ range) that don't exist in Athena's standard
    # vocab. If/when we add a registration workflow that inserts these custom
    # concepts into shared.concept, add the FK then.


def downgrade() -> None:
    # Foreign Keys
    op.drop_constraint('fk_cr_relationship', 'concept_relationship', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_cr_concept_2', 'concept_relationship', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_cr_concept_1', 'concept_relationship', schema='shared', type_='foreignkey')
    
    op.drop_constraint('fk_ds_denominator_unit', 'drug_strength', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_ds_numerator_unit', 'drug_strength', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_ds_amount_unit', 'drug_strength', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_ds_ingredient', 'drug_strength', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_ds_drug', 'drug_strength', schema='shared', type_='foreignkey')
    
    op.drop_constraint('fk_cs_language', 'concept_synonym', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_cs_concept', 'concept_synonym', schema='shared', type_='foreignkey')
    
    op.drop_constraint('fk_ca_descendant', 'concept_ancestor', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_ca_ancestor', 'concept_ancestor', schema='shared', type_='foreignkey')
    
    op.drop_constraint('fk_relationship_concept', 'relationship', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_vocabulary_concept', 'vocabulary', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_domain_concept', 'domain', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_concept_class_concept', 'concept_class', schema='shared', type_='foreignkey')
    
    op.drop_constraint('fk_concept_vocabulary', 'concept', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_concept_domain', 'concept', schema='shared', type_='foreignkey')
    op.drop_constraint('fk_concept_concept_class', 'concept', schema='shared', type_='foreignkey')

    # Indexes
    op.drop_index('idx_concept_relationship_id_3', table_name='concept_relationship', schema='shared')
    op.drop_index('idx_concept_relationship_id_2', table_name='concept_relationship', schema='shared')
    op.drop_index('idx_concept_relationship_id_1', table_name='concept_relationship', schema='shared')
    
    op.drop_index('idx_drug_strength_id_2', table_name='drug_strength', schema='shared')
    op.drop_index('idx_drug_strength_id_1', table_name='drug_strength', schema='shared')
    
    op.drop_index('idx_concept_synonym_id', table_name='concept_synonym', schema='shared')
    
    op.drop_index('idx_concept_ancestor_id_2', table_name='concept_ancestor', schema='shared')
    op.drop_index('idx_concept_ancestor_id_1', table_name='concept_ancestor', schema='shared')
    
    op.drop_index('idx_relationship_rel_id', table_name='relationship', schema='shared')
    op.drop_index('idx_vocabulary_vocabulary_id', table_name='vocabulary', schema='shared')
    op.drop_index('idx_domain_domain_id', table_name='domain', schema='shared')
    op.drop_index('idx_concept_class_class_id', table_name='concept_class', schema='shared')
    
    op.drop_index('idx_concept_vocabluary_id', table_name='concept', schema='shared')
    op.drop_index('idx_concept_domain_id', table_name='concept', schema='shared')
    op.drop_index('idx_concept_concept_id', table_name='concept', schema='shared')
    op.drop_index('idx_concept_code', table_name='concept', schema='shared')
    op.drop_index('idx_concept_class_id', table_name='concept', schema='shared')

    # Primary Keys
    op.drop_constraint('pk_relationship', 'relationship', schema='shared', type_='primary')
    op.drop_constraint('pk_vocabulary', 'vocabulary', schema='shared', type_='primary')
    op.drop_constraint('pk_domain', 'domain', schema='shared', type_='primary')
    op.drop_constraint('pk_concept_class', 'concept_class', schema='shared', type_='primary')
    op.drop_constraint('pk_concept', 'concept', schema='shared', type_='primary')

