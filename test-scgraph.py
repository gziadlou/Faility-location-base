from scgraph.geographs.us_freeway import us_freeway_geograph

freeway_output=us_freeway_geograph . get_shortest_path (
    origin_node ={"latitude": 34.1 ,"longitude": -118.2} ,
    destination_node ={"latitude": 40.7 ,"longitude": -74.0},
    output_units='mi'
)


print ('Length:',freeway_output ['length'])
print ('Path:',freeway_output ['coordinate_path'])