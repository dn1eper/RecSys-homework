from SPARQLWrapper import SPARQLWrapper, JSON
from json import dumps

sparql = SPARQLWrapper("https://query.wikidata.org/sparql") 

def other_director_films(film):
    """
    Возвращает список фильмов режиссера данного фильма
    """
    query = """ 
        SELECT ?film ?filmLabel
        WHERE {
            BIND("%s"@en AS ?recFilmLabel)
            
            ?f wdt:P31 wd:Q11424;
                    rdfs:label ?recFilmLabel;
                    wdt:P57 ?director.
            ?film wdt:P57 ?director

            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" } 
        }
    """
    sparql.setQuery(query % film)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

    
if __name__ == "__main__":
    results = other_director_films("Forrest Gump")
    out = []
    for result in results["results"]["bindings"]:
        out.append({ 
            "uri": result["film"]["value"],
            "label": result["filmLabel"]["value"]
        })

    print(dumps( out, indent=4))