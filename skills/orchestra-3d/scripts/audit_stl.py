"""Read-only STL topology audit. Run inside a fresh Blender background process."""
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh

WELD_MM = 0.000001


def inspect_mesh(bm):
    finite = all(math.isfinite(c) for v in bm.verts for c in v.co)
    dimensions = [max(v.co[i] for v in bm.verts) - min(v.co[i] for v in bm.verts)
                  for i in range(3)] if bm.verts and finite else None
    boundary = sum(e.is_boundary for e in bm.edges)
    nonmanifold_edges = sum(not e.is_manifold for e in bm.edges)
    nonmanifold_vertices = sum(not v.is_manifold for v in bm.verts)
    inconsistent = sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
    degenerate = sum(f.calc_area() <= WELD_MM ** 2 for f in bm.faces)
    remaining = set(bm.faces)
    shells = []
    while remaining:
        seed = remaining.pop()
        stack, faces = [seed], [seed]
        while stack:
            for edge in stack.pop().edges:
                for adjacent in edge.link_faces:
                    if adjacent in remaining:
                        remaining.remove(adjacent)
                        stack.append(adjacent)
                        faces.append(adjacent)
        # STL imports are triangles; fan triangulation also supports test polygons.
        origin = faces[0].verts[0].co
        volume = 0.0
        for face in faces:
            a = face.verts[0].co - origin
            for i in range(1, len(face.verts) - 1):
                b, c = face.verts[i].co - origin, face.verts[i + 1].co - origin
                volume += a.dot(b.cross(c)) / 6
        shells.append({'faces': len(faces), 'signed_volume_mm3': volume})
    passed = bool(bm.faces) and finite and not (
        nonmanifold_edges or nonmanifold_vertices or inconsistent or degenerate)
    passed = passed and all(math.isfinite(s['signed_volume_mm3']) and
                            abs(s['signed_volume_mm3']) > WELD_MM ** 3 for s in shells)
    # An inward shell may bound a valid cavity; containment needs separate review.
    orientation_review = any(s['signed_volume_mm3'] < 0 for s in shells)
    return {
        'topology_pass': passed, 'coordinate_unit': 'mm (assumed; STL is unitless)',
        'audit_pass': passed and not orientation_review,
        'orientation_review_required': orientation_review,
        'dimensions_mm': dimensions, 'vertices': len(bm.verts), 'faces': len(bm.faces),
        'boundary_edges': boundary, 'nonmanifold_edges': nonmanifold_edges,
        'nonmanifold_vertices': nonmanifold_vertices,
        'inconsistent_winding_edges': inconsistent, 'degenerate_faces': degenerate,
        'shells': shells, 'weld_tolerance_mm': WELD_MM,
        'unchecked': ['self_intersections', 'overlapping_shells', 'wall_thickness',
                      'dimensional_acceptance', 'physical_fit', 'strength', 'slicer'],
    }


def audit_file(path):
    path = Path(path).resolve(strict=True)
    if path.suffix.lower() != '.stl' or path.stat().st_size == 0:
        raise ValueError('Expected a nonempty .stl file')
    # Never inspect unrelated objects from the current scene.
    before = set(bpy.data.objects)
    bm = bmesh.new()
    try:
        imported = bpy.ops.wm.stl_import(filepath=str(path), global_scale=1.0,
                                         use_scene_unit=False, use_mesh_validate=False)
        if imported != {'FINISHED'}:
            raise ValueError('Blender did not finish STL import')
        objects = set(bpy.data.objects) - before
        for obj in objects:
            if obj.type == 'MESH':
                bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=WELD_MM)
        result = inspect_mesh(bm)
        result['file'] = str(path)
        return result
    finally:
        bm.free()
        for obj in set(bpy.data.objects) - before:
            mesh = obj.data if obj.type == 'MESH' else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if len(args) != 1:
        raise ValueError('Usage: blender --background --factory-startup '
                         '--python-exit-code 1 --python audit_stl.py -- part.stl')
    result = audit_file(args[0])
    print(json.dumps(result, indent=2, allow_nan=False))
    if not result['audit_pass']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
