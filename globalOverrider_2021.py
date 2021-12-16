import os
os.system('cls' if os.name == 'nt' else 'clear')

#                            globalOverrider.py 
#
#               Copyright (C) 2020, Will (The) Falcon WTFchannel
#                     https://www.youtube.com/c/willfalcon
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
## This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# ***** END GPL LICENCE BLOCK *****

import bpy

group_name = "GlobalMixer"
mixer_name = "Overrider"
mixer_label = "Cyberatonica"
MixerGlobalGroup = bpy.data.node_groups.get(group_name)

name_to_check = 'Material Output'
type_to_check = 'OUTPUT_MATERIAL'

print("\nMixerGlobalGroup:",MixerGlobalGroup,"\n")

# create a group
if MixerGlobalGroup == None :

    test_group = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')

    # create group inputs
    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-200,0)
    test_group.inputs.new('NodeSocketShader','MainShader')

    # create group outputs
    group_outputs = test_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (400,0)
    test_group.outputs.new('NodeSocketShader','MixedShader')

    # create three math nodes in a group
    node = test_group.nodes.new('ShaderNodeMixShader')
    node.location = (-200,-200)
    node.inputs[0].default_value = 1
    
    node2 = test_group.nodes.new('ShaderNodeBsdfDiffuse')
    node.location = (200,100)

    # link inputs
    test_group.links.new(group_inputs.outputs['MainShader'], node.inputs[1])
    #link output
    test_group.links.new(node.outputs[0], group_outputs.inputs['MixedShader'])
    test_group.links.new(node2.outputs[0], node.inputs[2])
    MixerGlobalGroup = test_group

    
    print('Global MIxer Created:', MixerGlobalGroup)
    
else:
    test_group = bpy.data.node_groups[group_name]
    print('Global MIxer Exists: ', test_group)

#####################################################################################
# ADD A MIXER GROUP
#####################################################################################
for mat in bpy.data.materials:
#   print("obj: ",mat.node_tree.nodes['Material Output'])
    nodes = mat.node_tree.nodes
    matOut = nodes.get("Material Output")

    for v in nodes:
        if (v.type == type_to_check and v.name != name_to_check):
            matOut = v
            print('I miss you so much - ', v.name)
        
    if nodes.get(mixer_name) != 'Undefined' and matOut != None:
        matInput = matOut.inputs
        mixer = nodes.new(type="ShaderNodeGroup")
        mixer.node_tree  = MixerGlobalGroup
        mixer.name = mixer_name
        mixer.label = mixer_label
        mixer.location = (matOut.location[0]-200, matOut.location[1])
        print(mixer_name," [created] ", mixer)
    else:
        print("....overrider already exists")

    nam = nodes.get(mixer_name)
    for v in nodes:
        if(nam != 'Undefined' and nam):
            s = v.name.split('.')
            l = len(s)
            if l > 1:
                if (s[0] == mixer_name):
                    nodes.remove(v)

#    print('\n\nlen:',len(matInput['Surface'].links), '\n')

    if matOut != None and matInput != None and len(matInput['Surface'].links):
        mylinks = mat.node_tree.links

        print('mixerOut = nodes.get(mixer_name)', nodes.get(mixer_name))

        mixerOut = nodes.get(mixer_name).outputs
        mixerIn = nodes.get(mixer_name).inputs

        old_link = matInput['Surface'].links[0].from_node
        
        if old_link.name != mixer_name:
            print("conected to: ",old_link.name)
            mylinks.new(mixerOut[0], matInput[0])
            old_link = mylinks.new(mixerIn[0], old_link.outputs[0])
        else:
            print("already connected to ", mixer_name)

    #print(mixerOut[0].from_node)
