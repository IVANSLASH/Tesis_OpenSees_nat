#!/usr/bin/env python3
"""
Debug script to manually check OpenSeesPy results after analysis
"""

import openseespy.opensees as ops
import sys
import input_data
import geometry
import sections
import slabs
import loads
import analysis

def debug_opensees_results():
    """Debug OpenSeesPy results by manually querying the model after analysis"""
    
    print("=" * 80)
    print("DEBUG: MANUAL OPENSEES RESULTS VERIFICATION")
    print("=" * 80)
    
    try:
        # Initialize model
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)
        
        # Quick setup using default values
        geometry_data = input_data.get_building_geometry_data(interactive=False)
        section_properties = sections.define_sections(interactive=False, material_choice="concreto_f21")
        
        # Create model components
        total_nodes = geometry.create_nodes(geometry_data, section_properties["E"], 0.49, 0, "-lMass")
        total_columns, column_elements_ids, next_ele_tag_after_columns = geometry.create_columns(
            geometry_data, section_properties["E"], 0, "-lMass",
            section_properties["A_col"], section_properties["Iz_col"],
            section_properties["Iy_col"], section_properties["J_col"]
        )
        total_beams_x, beam_elements_x_ids, total_beams_y, beam_elements_y_ids, next_ele_tag_after_beams = geometry.create_beams(
            geometry_data, section_properties["E"], 0, "-lMass",
            section_properties["A_viga"], section_properties["Iz_viga"],
            section_properties["Iy_viga"], section_properties["J_viga"],
            next_ele_tag_after_columns, total_nodes
        )
        total_slabs_elements, slab_elements_ids, next_ele_tag_after_slabs = slabs.create_slabs(
            geometry_data, section_properties, next_ele_tag_after_beams
        )
        
        # Apply loads
        load_intensities = loads.get_load_intensities(interactive=False, slab_config={'self_weight': 5.0})
        loads.apply_loads(
            geometry_data=geometry_data,
            load_intensities=load_intensities,
            beam_elements_x=beam_elements_x_ids,
            beam_elements_y=beam_elements_y_ids,
            total_nodes=total_nodes,
            interactive=False,
            combination="service"
        )
        
        # Run analysis
        print("\n1. RUNNING ANALYSIS...")
        analysis_success = analysis.run_analysis()
        print(f"   Analysis successful: {analysis_success}")
        
        if not analysis_success:
            print("   ❌ Analysis failed - cannot proceed with debugging")
            return
            
        print("\n2. CHECKING NODE DISPLACEMENTS...")
        
        # Check some representative nodes
        test_nodes = [17, 22, 30, 49, 54, 64]  # Various levels and positions
        for node in test_nodes:
            try:
                disp = ops.nodeDisp(node)
                coord = ops.nodeCoord(node)
                print(f"   Node {node} at ({coord[0]:.1f}, {coord[1]:.1f}, {coord[2]:.1f}):")
                print(f"      Ux={disp[0]:.6f}, Uy={disp[1]:.6f}, Uz={disp[2]:.6f}")
                print(f"      Rx={disp[3]:.6f}, Ry={disp[4]:.6f}, Rz={disp[5]:.6f}")
                print(f"      Max displacement: {max(abs(d) for d in disp[:3]):.6f} m")
            except Exception as e:
                print(f"   Error getting displacement for node {node}: {e}")
        
        print("\n3. CHECKING ELEMENT FORCES...")
        
        # Check some representative elements
        test_elements = [1, 25, 49, 73, 97, 121]  # Columns, beams, slabs
        for elem in test_elements:
            try:
                force = ops.eleForce(elem)
                elem_nodes = ops.eleNodes(elem)
                print(f"   Element {elem} (nodes {elem_nodes}):")
                if len(force) >= 12:  # Frame element
                    print(f"      Node I: N={force[0]:.2f}, Vy={force[1]:.2f}, Vz={force[2]:.2f}")
                    print(f"              T={force[3]:.2f}, My={force[4]:.2f}, Mz={force[5]:.2f}")
                    print(f"      Node J: N={force[6]:.2f}, Vy={force[7]:.2f}, Vz={force[8]:.2f}")
                    print(f"              T={force[9]:.2f}, My={force[10]:.2f}, Mz={force[11]:.2f}")
                else:
                    print(f"      Forces: {force}")
            except Exception as e:
                print(f"   Error getting force for element {elem}: {e}")
        
        print("\n4. CHECKING REACTION FORCES...")
        
        # Check base nodes (z=0)
        base_nodes = list(range(1, 17))  # First 16 nodes are at base
        total_vertical_reaction = 0.0
        for node in base_nodes:
            try:
                reaction = ops.nodeReaction(node)
                coord = ops.nodeCoord(node)
                print(f"   Node {node} at ({coord[0]:.1f}, {coord[1]:.1f}, {coord[2]:.1f}):")
                print(f"      Rx={reaction[0]:.2f}, Ry={reaction[1]:.2f}, Rz={reaction[2]:.2f} kN")
                print(f"      Mx={reaction[3]:.2f}, My={reaction[4]:.2f}, Mz={reaction[5]:.2f} kN⋅m")
                total_vertical_reaction += reaction[2]
            except Exception as e:
                print(f"   Error getting reaction for node {node}: {e}")
        
        print(f"\n   Total vertical reaction: {total_vertical_reaction:.2f} kN")
        
        print("\n5. CHECKING MODEL INTEGRITY...")
        
        all_nodes = ops.getNodeTags()
        all_elements = ops.getEleTags()
        print(f"   Total nodes in model: {len(all_nodes)}")
        print(f"   Total elements in model: {len(all_elements)}")
        
        # Check if there are any unconstrained nodes that should be constrained
        print(f"   Node range: {min(all_nodes)} to {max(all_nodes)}")
        print(f"   Element range: {min(all_elements)} to {max(all_elements)}")
        
        print("\n6. ANALYSIS VERIFICATION COMPLETE")
        print("   ✅ This debug confirms whether OpenSeesPy has valid results")
        
    except Exception as e:
        print(f"❌ Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_opensees_results()