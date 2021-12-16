import os
os.system('cls' if os.name == 'nt' else 'clear')

import bpy

group_name = "GlobalMixer"
mixer_name = "Overrider"
mixer_label = "Cyberatonica"
MixerGlobalGroup = bpy.data.node_groups

name_to_check = 'Material Output'
type_to_check = 'OUTPUT_MATERIAL'

ob = bpy.context.object

check_TYPES = ['SHADER']

for mat in bpy.data.materials:
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    matOut = nodes.get('Material Output')
    matInput = nodes.get("Material Input")

    nam = nodes.get(mixer_name)
    

    for v in nodes:
        if (v.type == type_to_check and v.name != name_to_check):
            v.name = name_to_check
        if(nam != 'Undefined' and nam):
            s = v.name.split('.')
            l = len(s)
            if l > 1:
                if (s[0] == mixer_name):
                    nodes.remove(v)


