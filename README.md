# Quarter 1 Project:
This project uses data from David Fenning's SOLEIL lab that creates solar cell samples in order to clean and transform the data, which is originally stored in a JSON file. The cleaned/transformed data are then saved as CSVs that allow it to be graphed in a Graph DBMS, Neo4j. The purpose of this task is to organize the data so that it is queryable once graphed with Neo4j.

This current iteration includes test data under test/testdata that is one sample of the data to show how our code works on "barebones" test data.

## To run the project, use run.py.

* The filepaths to the data are already hard-coded and available under the folder "test/testdata".
* The available targets for running ```python run.py <target>``` and the order of the targets are:
    * ```data```>```features```>```queries```
    * Alternatively, running the command ```python run.py test``` is equivalent to running each of the above targets sequentially.
* Running ```run.py``` cleans and transforms the data and creates queries in Neo4j's query language (Cypher) that allows for nodes and links to be graphed. Each graph in our implementation currently requires 6 queries to create and link all the nodes, so to help automate the process, the output of ```run.py``` is a Neo4j script-type file (.cypher file) that performs all of these queries in less inputs than doing so manually.
  * Our output file is named "output.cypher" and will be located in the project's root directory.
* In order to run this script, a docker container has to be created with Neo4j's docker image.
* To recreate and run our output, follow the steps below:
  * With Docker desktop open, in a local terminal, run ```docker pull neo4j``` and start a docker container with the Neo4j docker image.
  * Run the following command in a local terminal, which creates a Neo4j session and allows for access to the Neo4j Browser UI via port 7474 (localhost:7474)   
    * ```docker run --name neo4j_session -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/test neo4j:latest```
    * This browser is able to perform queries similar to SQL, but in Neo4j's graph query language instead, which will allow us to see the graphed data.
  * The next step is copying the "output.cypher" file into the docker container's root directory by running the following command in the local terminal
    * ```docker cp output.cypher neo4j_session:/output.cypher```
  * Once this is done, in the docker container terminal run the following commands
    * ```cd /``` to change to the root directory
    * ```cypher-shell -f output.cypher -u neo4j -p test``` Which will execute the script file and begin to generate the nodes and links of the graph.
  * Finally, in Neo4j's browser UI at localhost:7474, the following query can be entered to return the graph in order to see the output.
    * ```MATCH(n) RETURN n``` which returns all of the nodes and relationships, which should show the graphed sample. 
    
