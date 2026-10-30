import importlib.util
import copy
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('hierarchy',Path(__file__).resolve().parents[1]/'scripts/repair_skill_hierarchy.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

class HierarchyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.skills=self.root/'canonical';self.external=self.root/'external'
        self.roots={'canonical':self.skills,'hermes':self.external}
        self.write(self.skills/'when-test/SKILL.md','---\nname: when-test\ndescription: Test tasks\n---\n')
        self.write(self.skills/'when-test/references/routing.md','| Skill | Source | One-liner | Sub-skills |\n|---|---|---|---|\n| parent | hermes | old | - |\n')
        self.write(self.external/'parent/SKILL.md','---\nname: parent\ndescription: /R/o/u/t/e/ /t/h/i/s/ /t/a/s/k/\n---\n')
        self.write(self.external/'parent/child/SKILL.md','---\nname: child\ndescription: Child task\n---\n')
    def write(self,p,text):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    def plan(self,inventory=None):return h.plan(self.skills,self.roots,inventory=inventory or {})
    def test_seven_category_routes_are_unique_correct_and_idempotent(self):
        expected = {
            'productivity': 'when-using-personal-tools',
            'site-specific': 'when-using-personal-tools',
            'email': 'when-using-personal-tools',
            'smart-home': 'when-using-personal-tools',
            'mobile': 'when-shipping-code',
            'devops': 'when-shipping-code',
            'mlops': 'when-working-with-data',
        }
        assignments = {target: [] for target in set(expected.values())}
        assignments['when-test'] = list(expected) * 2 + ['unrelated-skill']
        h.route_categories(assignments)
        for name, target in expected.items():
            self.assertEqual([meta for meta, names in assignments.items() for n in names if n == name], [target])
        self.assertEqual(assignments['when-test'], ['unrelated-skill'])
        before = {meta: list(names) for meta, names in assignments.items()}
        h.route_categories(assignments)
        self.assertEqual(assignments, before)
    def test_family_discovery_precedes_alphabetical_leaves(self):
        nodes = {f'/skills/aaa-{i}/SKILL.md': {'name': f'aaa-{i}', 'description': 'leaf'} for i in range(15)}
        family = '/skills/productivity/SKILL.md'
        child = '/source/productivity/weekly-review-planning/SKILL.md'
        nodes[family] = {'name': 'productivity', 'description': 'Productivity procedures'}
        nodes[child] = {'name': 'weekly-review-planning', 'description': 'Weekly reset: commitments, stalled work, next-week plan.'}
        entries = [key for key in nodes if key != child]
        quick = h.quick_index(entries, nodes, {(family, child)})
        self.assertTrue(quick.startswith('- [productivity]'))
        for label in ['weekly-review-planning', 'commitments', 'stalled work', 'next-week plan']:
            self.assertIn(label, quick)
    def test_meta_first_outcomes_and_fallback_precedence(self):
        for name in ['when-using-personal-tools', 'when-nothing-else-fits']:
            self.write(self.skills/name/'SKILL.md', f'name: {name}\ndescription: old\n')
            self.write(self.skills/name/'references/routing.md', '')
        out,_ = self.plan()
        contract = out[self.skills/'when-building-or-fixing-agents/references/meta-first.md']
        self.assertIn('weekly reviews, commitments, stalled projects, next-week planning, calendar and productivity', contract)
        self.assertIn('only after the specific routes have no relevant match', contract)
        self.assertLess(contract.index('[when-using-personal-tools]'), contract.index('[when-nothing-else-fits]'))
        self.assertNotIn(self.skills/'when-nothing-else-fits/SKILL.md', out)
        self.assertIn('only after the specific routes have no relevant match', contract)
    def test_path_resolution_prefers_canonical(self):
        self.write(self.skills/'parent/SKILL.md','description: canonical\n')
        self.assertEqual(h.resolve('parent',self.roots),self.skills/'parent/SKILL.md')
    def test_flattened_existing_category_fails_closed(self):
        self.write(self.skills/'lost-family/SKILL.md',h.MARKER+'\ndescription: Existing family\n')
        with self.assertRaisesRegex(ValueError,'Unrouted existing categories: lost-family'):
            self.plan()
    def test_explicit_nested_source_survives_rerender(self):
        nested=self.external/'family/leaf/SKILL.md'
        self.write(nested,'description: Exact nested source\n')
        self.write(self.skills/'when-test/references/routing.md',f'| leaf | [leaf]({nested}) | desc | - |\n')
        out,m=self.plan();h.apply(out,self.root/'backups')
        self.write(self.external/'leaf/SKILL.md','description: Unrelated same basename\n')
        out2,m2=self.plan()
        self.assertIn(str(nested),[n['source'] for n in m2['nodes']])
        self.assertNotIn(str(self.skills/'leaf/SKILL.md'),[n['source'] for n in m2['nodes']])
        self.assertEqual(m,m2)
    def test_explicit_missing_source_fails_closed(self):
        self.write(self.skills/'when-test/references/routing.md',f'| leaf | [leaf]({self.external}/missing/SKILL.md) | desc | - |\n')
        with self.assertRaisesRegex(ValueError,'explicit source'):
            self.plan()
    def test_moved_category_preserves_explicit_source(self):
        nested=self.external/'family/productivity/SKILL.md'
        self.write(nested,'description: Exact nested source\n')
        self.write(self.external/'productivity/SKILL.md','description: Unrelated basename\n')
        self.write(self.skills/'when-using-personal-tools/SKILL.md','description: Personal tasks\n')
        self.write(self.skills/'when-using-personal-tools/references/routing.md','')
        self.write(self.skills/'when-test/references/routing.md',f'| productivity | [productivity]({nested}) | desc | - |\n')
        _,m=self.plan()
        self.assertIn([str(self.skills/'when-using-personal-tools/SKILL.md'),str(nested)],m['edges'])
        self.assertNotIn(str(self.external/'productivity/SKILL.md'),[n['source'] for n in m['nodes']])
    def test_missing_target(self):
        _,m=self.plan();Path(m['nodes'][0]['source']).unlink()
        with self.assertRaisesRegex(ValueError,'Missing target'):h.validate(m)
    def test_self_cycle(self):
        _,m=self.plan();key=m['nodes'][0]['id'];m['edges'].append([key,key])
        with self.assertRaisesRegex(ValueError,'Cycle'):h.validate(m)
    def test_duplicate_edges(self):
        _,m=self.plan();m['edges'].append(m['edges'][0])
        with self.assertRaisesRegex(ValueError,'Duplicate edges'):h.validate(m)
    def test_duplicate_physical_target_rejected(self):
        _,m=self.plan();m=copy.deepcopy(m)
        m['nodes'][1]['resolved_target']=m['nodes'][0]['resolved_target']
        with self.assertRaisesRegex(ValueError,'Duplicate physical ownership'):h.validate(m)
    def test_invalid_level_and_edge_rejected(self):
        _,m=self.plan();m=copy.deepcopy(m)
        m['nodes'][-1]['level']=4
        with self.assertRaisesRegex(ValueError,'Invalid three-tier levels'):h.validate(m)
        _,m=self.plan();m=copy.deepcopy(m)
        meta=next(n['id'] for n in m['nodes'] if n['level']==1)
        child=next(n['id'] for n in m['nodes'] if n['level']==3)
        m['edges'].append([meta,child])
        with self.assertRaisesRegex(ValueError,'Invalid three-tier edge'):h.validate(m)
    def test_orphan_and_owner_rejected(self):
        _,m=self.plan();m=copy.deepcopy(m)
        m['edges'].pop()
        with self.assertRaisesRegex(ValueError,'Invalid or duplicate owner'):h.validate(m)
        _,m=self.plan();orphan=self.skills/'orphan/SKILL.md'
        self.write(orphan,'description: orphan\n')
        with self.assertRaisesRegex(ValueError,'Canonical orphan'):h.validate(m)
    def test_corrupt_description_repaired_and_rejected(self):
        _,m=self.plan();self.assertTrue(any(n['description']=='Route this task' for n in m['nodes']))
        m['nodes'][0]['description']='/R/o/u/t/e/ /t/h/i/s/ /t/a/s/k/'
        with self.assertRaisesRegex(ValueError,'Corrupted description'):h.validate(m)
    def test_unresolved_declared_child_fails(self):
        with self.assertRaisesRegex(ValueError,'Unresolved children.*absent'):
            self.plan({'parent':{'path':str(self.external/'parent'),'children':['parent/absent']}})
    def test_resource_and_self_duplicates_excluded(self):
        self.write(self.external/'parent/references/SKILL.md','description: resource\n')
        self.write(self.external/'parent/skills/parent/SKILL.md','description: self\n')
        _,m=self.plan();self.assertEqual(len(m['edges']),2)
    def test_descendant_not_replaced_by_global_basename(self):
        self.write(self.external/'child/SKILL.md','description: unrelated global child\n')
        _,m=self.plan()
        self.assertIn(str(self.external/'parent/child/SKILL.md'),[n['source'] for n in m['nodes']])
        self.assertNotIn(str(self.skills/'child/SKILL.md'),[n['source'] for n in m['nodes']])
    def test_old_table_unresolved_child_fails(self):
        self.write(self.skills/'when-test/references/routing.md','| parent | hermes | desc | absent |\n')
        with self.assertRaisesRegex(ValueError,'Unresolved children.*absent'):
            self.plan()
    def test_generated_category_updates_when_source_child_changes(self):
        (self.external/'parent/SKILL.md').unlink()
        out,_=self.plan();h.apply(out,self.root/'backups')
        self.write(self.external/'parent/child/SKILL.md','description: new child responsibility\n')
        out,_=self.plan()
        self.assertIn('new child responsibility',out[self.skills/'parent/SKILL.md'])
        self.assertNotEqual((self.skills/'parent/SKILL.md').read_text(),out[self.skills/'parent/SKILL.md'])
    def test_symlinked_destination_ancestor_rejected(self):
        (self.external/'parent/SKILL.md').unlink()
        (self.skills/'parent').symlink_to(self.external/'parent',target_is_directory=True)
        out,_=self.plan()
        with self.assertRaisesRegex(ValueError,'Destination outside'):
            h.apply(out,self.root/'backups')
        self.assertFalse((self.external/'parent/SKILL.md').exists())
    def test_source_drift_aborts_before_writes(self):
        out,_=self.plan()
        original=(self.skills/'when-test/SKILL.md').read_bytes()
        self.write(self.external/'parent/child/SKILL.md','description: drift\n')
        with self.assertRaisesRegex(ValueError,'Source drift'):
            h.apply(out,self.root/'backups')
        self.assertEqual(original,(self.skills/'when-test/SKILL.md').read_bytes())
        self.assertFalse((self.root/'backups').exists())
    def test_category_and_idempotence(self):
        (self.external/'parent/SKILL.md').unlink()
        out,m=self.plan();before=(self.external/'parent/child/SKILL.md').read_bytes()
        backup=h.apply(out,self.root/'backups');self.assertIsNotNone(backup)
        out2,m2=self.plan();self.assertEqual(m,m2)
        self.assertTrue(all(p.read_text()==t for p,t in out2.items()))
        self.assertIsNone(h.apply(out2,self.root/'backups'))
        self.assertEqual(before,(self.external/'parent/child/SKILL.md').read_bytes())

    def test_normalization_shadows_direct_assignment_owned_by_family(self):
        meta = str(self.skills/'when-test/SKILL.md')
        family = str(self.external/'parent/SKILL.md')
        child = str(self.external/'parent/child/SKILL.md')
        nodes = {path: {'id': path, 'source': path, 'resolved_target': path,
                        'name': Path(path).parent.name, 'level': level}
                 for path, level in [(meta, 1), (family, 2), (child, 2)]}
        normalized, edges, aliases, shadowed = h.normalize_graph(
            nodes, {(meta, family), (meta, child), (family, child)}, self.skills)
        self.assertEqual(aliases, [])
        self.assertEqual(edges, {(meta, family), (family, child)})
        self.assertEqual(normalized[child]['level'], 3)
        self.assertEqual(len(shadowed), 1)
        self.assertEqual(shadowed[0]['alias'], child)

    def test_manifest_retains_alias_audit_records(self):
        _, manifest = self.plan()
        self.assertEqual(manifest['schema_version'], 2)
        self.assertIn('physical_aliases', manifest)
        self.assertIn('shadowed_assignments', manifest)
    def test_retirement_note_is_not_treated_as_skill_and_is_preserved(self):
        table = self.skills/'when-test/references/routing.md'
        table.write_text(table.read_text() + '| (retired 2026-09-24 - old-router) | - | Replaced by JevRouter | - |\n')
        output, manifest = self.plan()
        self.assertIn('## Preserved notes', output[table])
        self.assertIn('(retired 2026-09-24 - old-router)', output[table])
        self.assertNotIn('(retired 2026-09-24 - old-router)', [n['name'] for n in manifest['nodes']])

    def test_graph_audit_fails_on_canonical_orphan(self):
        _, manifest = self.plan()
        nodes = {node['id']: node for node in manifest['nodes']}
        edges = {tuple(edge) for edge in manifest['edges']}
        self.assertEqual(h.audit_graph(self.skills, nodes, edges)['status'], 'PASS')
        orphan = self.skills/'orphan/SKILL.md'
        self.write(orphan, '---\nname: orphan\ndescription: Unrouted task\n---\n')
        report = h.audit_graph(self.skills, nodes, edges)
        self.assertEqual(report['status'], 'RED')
        self.assertEqual(report['canonical_orphans'], [str(orphan.resolve())])
        self.assertIn('canonical_orphans', report['failures'])

    def test_audit_requires_materialized_routes(self):
        output, manifest = self.plan()
        nodes = {node['id']: node for node in manifest['nodes']}
        edges = {tuple(edge) for edge in manifest['edges']}
        structural = h.audit_graph(self.skills, nodes, edges)
        before = h.audit_materialization(structural, output)
        self.assertEqual(before['structural_status'], 'PASS')
        self.assertEqual(before['status'], 'RED')
        self.assertEqual(before['materialized_status'], 'DRIFT')
        h.apply(output, self.root/'backups')
        after = h.audit_materialization(structural, output)
        self.assertEqual(after['status'], 'PASS')

    def test_authored_meta_skill_rewrite_is_protected(self):
        path = self.skills/'when-test/SKILL.md'
        self.assertEqual(h.protected_meta_rewrites({path: 'replacement'}), [str(path)])
        self.assertEqual(h.protected_meta_rewrites({path: path.read_text()}), [])

    def test_revenue_family_owns_only_canonical_revenue_siblings(self):
        meta = self.skills/'rig-revenue-meta/SKILL.md'
        child = self.skills/'rig-revenue-ai-citation-gaps/SKILL.md'
        other = self.skills/'unrelated/SKILL.md'
        for path in (meta, child, other):
            self.write(path, f'description: {path.parent.name}\n')
        self.write(meta, f'description: Revenue router\n## Routing table\nRead {child.parent.name} for citation gaps.\n## Step 1\n')
        self.assertEqual(h.canonical_family_children('rig-revenue-meta', self.skills), [child])
        self.assertEqual(h.canonical_family_children('unrelated', self.skills), [])

    def test_website_family_owns_only_its_subskills(self):
        parent = self.skills/'web-color/SKILL.md'
        child = self.skills/'web-color-contrast/SKILL.md'
        unrelated = self.skills/'web-layout-grid/SKILL.md'
        for path in (parent, child, unrelated):
            self.write(path, f'description: {path.parent.name}\n')
        self.write(parent, f'description: Color router\nRead {child.parent.name} for contrast.\n')
        self.assertEqual(h.canonical_family_children('web-color', self.skills), [child])
        self.assertEqual(h.canonical_family_children('web-unknown', self.skills), [])

if __name__=='__main__':unittest.main()
