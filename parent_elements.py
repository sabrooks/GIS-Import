'''Identifies the parent element of an element
elements are dictionaries with the key geometry
Create a defaultdict of starting points. 
'''

from collections import defaultdict
import logging
import fiona

LOG_FILE = 'parent.log'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

def get_end_points(gdb, layer) -> defaultdict:
    '''
    Returns a defaultdict of starting points in the format:
    (x,y):[GlobalID]
    '''
    layer_gen = fiona.open(gdb, layer=layer)
    # For each feature, add to defaultdict.
    points = defaultdict(list)
    for feature in list(layer_gen):
        geo = feature['geometry']
        global_id = feature['properties']['GlobalID']
        # End points are in the format (x,y)
        # Points only have a single point
        # Segments are lists of points [(x1,y1), (x2, y2, .. ]
        end_point = (geo['coordinates'] if geo['type'] == 'Point'
                          else geo['coordinates'][0][-1])
        points[end_point].append(global_id)
    return points

def search_end_points(gdb, layer, end_points: defaultdict) -> list:
    '''Searches for elements with end_points that match starting_points'''
    
    def end_gen(feature, end_points: defaultdict):
        geo = feature['geometry']
        feature_start = (geo['coordinates'] if geo['type'] == 'Point'
                         else geo['coordinates'][0][0])
        # End points are in the format (x,y)
        # Points only have a single point
        # Segments are lists of points [(x1,y1), (x2, y2, .. ]
        try:
            parent = end_points[feature_start]
            yield parent
        except:
            logging.debug(feature['id'] + 'Parent Not Found')

    layer_gen = fiona.open(gdb, layer=layer)
    return (end_gen(feature, end_points) for feature in layer_gen)
