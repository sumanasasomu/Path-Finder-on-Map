# !/usr/bin/python
from configparser import ConfigParser
import psycopg2
import pickle
import os

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return db

def adjList():
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()

        f1 = "SELECT rid, concat(y,',',x) as concatval1 from (SELECT osm_id as rid, ST_Y(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as y, ST_X(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as x FROM planet_osm_line WHERE (highway = 'primary' OR highway = 'secondary' OR highway = 'tertiary' OR highway = 'motorway' OR highway = 'unclassified' OR highway = 'trunk' OR highway = 'primary_link' OR highway = 'secondary_link' OR highway = 'tertiary_link' OR highway = 'motorway_link' OR highway = 'trunk_link') OR (highway = 'service' and oneway = 'yes') order by osm_id) as f1;"
        f2 = "SELECT row_number() over (), distinctnodes,rid from (select distinctnodes,rid from (select distinct on (concatval2) concatval2 as distinctnodes, temporder, rid from (select row_number() over() as temporder, rid, concat(y,',',x) as concatval2 from (SELECT osm_id as rid, ST_Y(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as y, ST_X(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as x FROM planet_osm_line WHERE (highway = 'primary' OR highway = 'secondary' OR highway = 'tertiary' OR highway = 'motorway' OR highway = 'unclassified' OR highway = 'trunk' OR highway = 'primary_link' OR highway = 'secondary_link' OR highway = 'tertiary_link' OR highway = 'motorway_link' OR highway = 'trunk_link') OR (highway = 'service' and oneway = 'yes')) as table2) as table3) as table4 order by rid,temporder) as f2;"

        cur.execute("SELECT final1.rid,final1.concatval1,final2.row_number from (select rid,concatval1,temp1 from(select row_number() over() as temp1, rid, concat(y,',',x) as concatval1 from (SELECT osm_id as rid, ST_Y(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as y, ST_X(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as x FROM planet_osm_line WHERE (highway = 'primary' OR highway = 'secondary' OR highway = 'tertiary' OR highway = 'motorway' OR highway = 'unclassified' OR highway = 'trunk' OR highway = 'primary_link' OR highway = 'secondary_link' OR highway = 'tertiary_link' OR highway = 'motorway_link' OR highway = 'trunk_link') OR (highway = 'service' and oneway = 'yes') order by osm_id) as f1) as f12) as final1, (select row_number() over (), distinctnodes,rid from (select distinctnodes,rid from (select distinct on (concatval2) concatval2 as distinctnodes, temporder, rid from (select row_number() over() as temporder, rid, concat(y,',',x) as concatval2 from (SELECT osm_id as rid, ST_Y(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as y, ST_X(ST_AsText(ST_PointN(way,generate_series(1,ST_NPoints(way))))) as x FROM planet_osm_line WHERE (highway = 'primary' OR highway = 'secondary' OR highway = 'tertiary' OR highway = 'motorway' OR highway = 'unclassified' OR highway = 'trunk' OR highway = 'primary_link' OR highway = 'secondary_link' OR highway = 'tertiary_link' OR highway = 'motorway_link' OR highway = 'trunk_link') OR (highway = 'service' and oneway = 'yes')) as table2) as table3) as table4 order by rid,temporder) as f2) as final2 where final1.concatval1 = final2.distinctnodes order by final1.temp1;")
        
        rows = cur.fetchall()

        print("The number of parts: ", cur.rowcount)
        
        end_lat = 17.2406919
        end_lon = 78.4329069
        end_way = 29113368
        end_node_id = 69555

        start_way = 262821911
        start_lat = 17.5473641
        start_lon = 78.5724988
        start_node_id = 74037
        adj_list = {}
        node_long_lat = {} # nodeid -> 'longitute,lattitude'

        for i in range(cur.rowcount-1):
            if rows[i][0] == end_way:
                print(rows[i])
            if rows[i][2] not in adj_list.keys():
                adj_list[rows[i][2]] = []
                node_long_lat[rows[i][2]] = rows[i][1]
            if rows[i+1][2] not in adj_list.keys():
                adj_list[rows[i+1][2]] = []
                node_long_lat[rows[i+1][2]] = rows[i+1][1]
            if rows[i][0] == rows[i+1][0]:
                if rows[i+1][2] not in adj_list[rows[i][2]]:
                    adj_list[rows[i][2]].append(rows[i+1][2])
                if rows[i][2] not in adj_list[rows[i+1][2]]:
                    adj_list[rows[i+1][2]].append(rows[i][2])
        
        with open("node_long_lat.pickle","wb") as f:
            pickle.dump(node_long_lat,f)    
        with open("adj_list.pickle","wb") as f:
            pickle.dump(adj_list,f)
        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    if "node_long_lat.pickle" and "adj_list.pickle" not in os.listdir("./"):
        adjList()
    else:
        print("Pickel files already exists")