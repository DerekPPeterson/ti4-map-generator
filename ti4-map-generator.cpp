#include <iostream>
#include <fstream>
#include <list>
#include <map>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <time.h>
#include <exception>

#include "json.hpp"

#define BACKWARD_HAS_BFD 1
#include "backward-cpp/backward.hpp"

using json = nlohmann::json;

using namespace std;

enum PlanetTrait
{
    NO_TRAIT,
    CULTURAL,
    INDUSTRIAL,
    HAZARDOUS
};

map<string, PlanetTrait> trait_key = {
    {"NO_TRAIT", NO_TRAIT},
    {"CULTURAL", CULTURAL},
    {"HAZARDOUS", HAZARDOUS},
    {"INDUSTRIAL", INDUSTRIAL}
};

enum TechColor
{
    NO_COLOR,
    BLUE,
    RED,
    GREEN,
    YELLOW
};

map<string, TechColor> tech_key = {
    {"NO_TECH", NO_COLOR},
    {"BLUE", BLUE},
    {"RED", RED},
    {"GREEN", GREEN},
    {"YELLOW", YELLOW}
};

enum Wormhole
{
    NO_WORMHOLE,
    ALPHA,
    BETA,
    DELTA
};

map<string, Wormhole> wormhole_key = {
    {"NO_WORMHOLE", NO_WORMHOLE},
    {"ALPHA", ALPHA},
    {"BETA", BETA},
    {"DELTA", DELTA}
};

enum Anomaly
{
    NO_ANOMALY,
    EMPTY,
    GRAVITY_RIFT,
    NEBULA,
    SUPERNOVA,
    ASTEROID_FIELD
};

map<string, Anomaly> anomaly_key = {
    {"NO_ANOMALY", NO_ANOMALY},
    {"EMPTY", EMPTY},
    {"GRAVITY_RIFT", GRAVITY_RIFT},
    {"NEBULA", NEBULA},
    {"SUPERNOVA", SUPERNOVA},
    {"ASTEROID_FIELD", ASTEROID_FIELD},
};

typedef struct Planet
{
    string name;
    int resources;
    int influence;
    PlanetTrait trait;
    TechColor tech;
} Planet;

typedef struct Location
{
    int i;
    int j;
} Location;

class Tile
{
    int number;
    Wormhole wormhole;
    list<Planet> planets;
    Anomaly anomaly;
    Location location;

    public:
    Tile(int);
    Tile(int, list<Planet>, Wormhole, Anomaly);
    string get_description_string() const;
    int get_number();
    void set_location(Location);
};

int Tile::get_number() {
    return number;
}

void Tile::set_location(Location l) {
    location = l;
}

string Tile::get_description_string() const {
    ostringstream desc;
    desc << "Tile " << number << " - ";
    for (auto it = planets.begin(); it != planets.end(); it++) {
        if (it != planets.begin()) {
            desc << ", ";
        }
        desc << it->name;
    }

    return desc.str();
}

std::ostream& operator<< (std::ostream &out, Tile const& tile) {
    out << tile.get_description_string();
    return out;
}

Tile::Tile(int n)
{
    number = n;
}


Tile::Tile(int n, list<Planet> p, Wormhole w, Anomaly a)
{
    number = n;
    planets = p;
    wormhole = w;
    anomaly = a;
}


class Galaxy
{
    list<Tile> tiles;
    Tile *grid[7][7]; // Locations of tiles
    Tile *mecatol;
    list<Tile*> home_systems;
    list<Tile*> movable_systems;
    Tile boundary_tile;

    void import_tiles(string tile_filename);
    void create_home_tiles(int n);
    void initialize_grid();
    void place_tile(Location location, Tile*);

    public:
    Galaxy(string tile_filename);
    void print_grid();
};

Galaxy::Galaxy(string tile_filename)
    : boundary_tile(0)
{
    import_tiles(tile_filename);
    create_home_tiles(6);
    initialize_grid();

    for (auto i : tiles) {
        cout << i << endl;
    }
}

void Galaxy::place_tile(Location l, Tile* tile) 
{
    if (tile) {
        tile->set_location(l);
    }
    grid[l.i][l.j] = tile;
}

Planet create_planet_from_json(json j)
{
    Planet new_planet;

    new_planet.name = j["name"];
    new_planet.resources = j["resources"];
    new_planet.influence = j["influence"];

    new_planet.trait = trait_key.at(j["trait"]);
    new_planet.tech = tech_key.at(j["tech"]);

    return new_planet;
}

Tile create_tile_from_json(json j)
{
    int number = j["number"];
    Wormhole wormhole = wormhole_key.at(j["wormhole"]);
    Anomaly anomaly = anomaly_key.at(j["anomaly"]);

    // Create planet list
    json planet_list = j["planets"];
    list<Planet> planets;
    for (json::iterator it = planet_list.begin(); it != planet_list.end(); it++) {
        planets.push_back(create_planet_from_json(it.value()));
    }

    Tile new_tile = Tile(number, planets, wormhole, anomaly);
    return new_tile;
}

void Galaxy::import_tiles(string tile_filename)
{
    // Parse tile json
    // TODO error handle parse errors file not exist etc
    json tile_json;
    ifstream json_file;
    cerr << "Importing tiles from " << tile_filename << endl;
    json_file.open(tile_filename);
    try {json_file >> tile_json;} 
    catch (...) {
        cerr << "Error loading/parsing " << tile_filename << endl;
        exit(-1);
    }
    json_file.close();

    // Create list of tiles
    json tile_list = tile_json["tiles"];
    for (json::iterator it = tile_list.begin(); it != tile_list.end(); it++) {
        tiles.push_back(create_tile_from_json(it.value()));
        movable_systems.push_back(&tiles.back());
    }
    
    // Save a pointer to mecatol rex
    tiles.push_back(create_tile_from_json(tile_json["mecatol"]));
    mecatol = &tiles.back();

    cerr << "Loaded " << tiles.size() << " tiles" << endl;
}

void Galaxy::create_home_tiles(int n) {
    for (int i = 0; i < n; i++) {
        list<Planet> no_planets;
        Tile new_tile = Tile(-i - 1, no_planets, NO_WORMHOLE, NO_ANOMALY);
        tiles.push_back(new_tile);
        home_systems.push_back(&tiles.back());
    }
}

template <class t>
list<t> get_shuffled_list(list<t> l) {
    list<t> new_list;
    new_list = l;
    random_shuffle(l.begin(), l.end());
    return l;
}

void Galaxy::initialize_grid() {
    for (int i = 0; i < 7;i++) {
        for (int j = 0; j < 7; j++) {
            place_tile({i, j}, NULL);
        }
    }
    for (int i = 0; i < 3;i++) {
        for (int j = 4 + i; j < 7; j++) {
            place_tile({i, j}, &boundary_tile);
        }
    }
    for (int j = 0; j < 3;j++) {
        for (int i = 4 + j; i < 7; i++) {
            place_tile({i, j}, &boundary_tile);
        }
    }

    // Place Mecatol at centre of galaxy
    place_tile({3, 3}, mecatol);

    // Place home systems // TODO for other counts than 6p
    int corners[6][2] = {{0,0},{0,3},{3,6},{6,6},{6,3},{3,0}};
    int i = 0;
    for (auto it : home_systems) {
        place_tile({corners[i][0], corners[i][1]}, it);
        i++;
    }

    // Shuffle tiles
    vector<Tile*> random_tiles;
    for (auto it : movable_systems) {
        random_tiles.push_back(it);
    }
    random_shuffle(random_tiles.begin(), random_tiles.end());

    for (int i = 0; i < 7;i++) {
        for (int j = 0; j < 7; j++) {
            if (not grid[i][j]) {
                place_tile({i, j}, random_tiles.back());
                random_tiles.pop_back();
            }
        }
    }
}


void Galaxy::print_grid() {
    int I = 7;
    int J = 7;
    for (int i = 0; i < I; i++) {
        for (int i_pad = 0; i_pad < I - i; i_pad++) {
            cout << "  ";
        }
        for (int j = 0; j < J; j++) {
            if (grid[i][j] and grid[i][j] != &boundary_tile) {
                printf(" %02d ", grid[i][j]->get_number());
            } else {
                cout << "    ";
            }
        }
        cout << endl << endl;
    }
}

//float Galaxy::evaluate_grid() {
//    float score;
//    return score;
//}

int main() {

    srand(time(NULL));

    Galaxy galaxy("tiles.json");
    galaxy.print_grid();

    return 0;
}
