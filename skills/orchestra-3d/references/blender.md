# Blender: reproducibility, units and export

Discover the executable using PATH, the OS application inventory or normal installation directories. Check `--version`; inspect the installed operator RNA/help when an API differs. Use existing official/vendor integrations first. Do not install Blender, add-ons or a slicer merely because they are missing; explain the missing capability and use existing tools where adequate. Do not claim a fallback produced a `.blend` if it did not.

Run generated scripts in a fresh background process, with an error exit code:

```text
<blender> --background --factory-startup --python-exit-code 1 --python <project-script.py> -- <project-arguments>
```

`--factory-startup` applies to the new process, not the user's active session. Do not run arbitrary embedded scripts from untrusted `.blend` files or enable automatic execution. Discover and use available computer-use tooling for GUI tasks; no mandatory MCP server or third-party skill is needed. Open a generated `.blend` in a separate GUI process when possible, without replacing unsaved work. If only background execution is available, disclose that the GUI was not opened and deliver a preview.

## One explicit unit convention

For new Blender-generated print projects, use **one coordinate unit = one millimeter**:

```python
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'
# A 20 mm side is 20 coordinate units, not 0.020.
bpy.ops.wm.stl_export(
    filepath=str(stl_path),
    export_selected_objects=True,
    apply_modifiers=True,
    global_scale=1.0,
    use_scene_unit=False,
    forward_axis='Y', up_axis='Z',
)
```

STL has no unit metadata. Record that numeric STL coordinates represent mm. Setting scene units alone does not rescale existing geometry. For imported meter/inch models, measure known features and convert once; do not silently apply this convention to an existing scene. Selection must contain only the intended printable mesh objects. Check export returned `FINISHED`, nonempty file, and reimport bounds. Avoid accidental 1000x scaling caused by combining scene-unit conversion with already-mm coordinates. Use an explicit collection for print parts; apply geometric modifiers to export while preserving editable source. Resolve instances/curves to meshes on export copies if needed.

## Actual exported-file audit

```text
<blender> --background --factory-startup --python-exit-code 1 --python <installed-skill>/scripts/audit_stl.py -- <part.stl>
```

The helper imports the actual file, checks finite bounds, degeneracy, manifold edges/vertices, consistent winding, disconnected shells and signed volume per shell. It welds coincident STL triangle vertices at `0.000001` coordinate units (mm under the convention above). That tolerance can merge finer geometry; it is for audit only and never saves a repaired STL. A nonzero exit means failed topology/input checks; read the JSON and process log. Compare `dimensions_mm` to the brief with an explicit design tolerance. Evaluate shell count against the expected part count; disconnected shells are reported, not automatically rejected. Multiple intended parts should normally be separate files.

`topology_pass` covers topology and nonzero volume magnitude; `audit_pass` additionally requires no inward shell needing review. Exit 2 means failed checks or required orientation review. A negative signed volume may indicate an inverted outer shell OR a correctly oriented cavity: verify nesting and material boundaries before changing normals. Never automatically flip every shell positive. Cavity containment is not solved by this helper.

This is not a self-intersection or thickness solver. Inspect those separately using available mesh analysis and slicer tools. Do not turn an unchecked field into a pass. Preserve previous revisions and include the Blender version in the project report.

Official references, to consult when API or units are uncertain:
- https://docs.blender.org/api/current/bpy.ops.wm.html
- https://docs.blender.org/manual/en/latest/files/import_export/stl.html
