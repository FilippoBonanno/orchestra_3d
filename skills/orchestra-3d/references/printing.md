# Print acceptance

## Geometry and fit

- Check the exported file's mm envelope, expected shells/parts, boundary orientation and finite positive material volume. Cavity boundaries can correctly have negative signed volume; verify containment before reversing any normals. Inspect holes, wall thickness, self-intersections, internal overlapping solids and fragile details with an available geometric tool and/or cross-sections. Joining objects does not boolean-union their solids; a manifold edge result can still hide overlapping shells.
- Use the actual process/nozzle or resin profile for minimum walls and details. Do not advertise one universal wall thickness, overhang limit or fit clearance. If unknown, document a provisional value and its dependency on material, orientation and calibration.
- Specify clearance as radial/per-side or diametral/total; for example, a 20.0 mm shaft in a 20.4 mm hole has 0.4 mm diametral clearance, 0.2 mm per side. This is an arithmetic example, not a universal fit recommendation. Use a small fit coupon for uncertain mating parts instead of wasting a full print.
- For load-bearing pieces, consider layer direction, stress concentrations, fillets, fasteners and material behavior. A render and mesh audit cannot verify mechanical strength.

## Manufacturing

With a known printer/profile: check build volume including orientation and support/brim space, bed contact, feature visibility in layers, islands, bridging, overhangs, support access/removal, seams and mating surfaces. Split oversized parts only when required, preserving assembly references and interface clearances. For resin hollow parts consider trapped volumes, drainage, venting and cleaning access; for FDM consider anisotropy and extrusion width. Derive recommendations from the selected process, not from an assumed printer.

Use an installed slicer through its supported interface. Inspect actual layer output; give estimates only when produced by the stated profile and label them estimates. Generic G-code can command wrong temperatures, travel or machine limits: generate machine instructions only when requested and with the exact machine profile. Never start a print solely because preparation completed.

## Delivery report

Keep this short and project-specific:

```text
Status: concept only / mesh checked; slicer unverified / slicer checked for <profile>
Files: editable source, STL per part, preview, parameters/script if generated
Size: X x Y x Z mm; STL numeric coordinates interpreted as mm
Fit: measured references, clearance convention, assumptions
Checks: actual mesh findings, visual inspection, slicer/profile if run
Printing: proposed orientation/supports; material/profile assumptions
Unverified: thickness/intersections/fit/strength or other checks not performed
```

Do not write "ready to print" merely because an STL exists or has no boundary edges. Report any blocker before claiming completion.
