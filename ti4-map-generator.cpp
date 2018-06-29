#include <iostream>
#include <fstream>
#include <list>
#include <map>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <time.h>
#include <exception>
#include <cmath>
#include <iterator>

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

static map<string, PlanetTrait> trait_key = {
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

static map<string, TechColor> tech_key = {
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

static map<string, Wormhole> wormhole_key = {
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

static map<string, Anomaly> anomaly_key = {
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

    Location operator+(Location a) {
        struct Location new_location;
        new_location.i = this->i + a.i;
        new_location.j = this->j + a.j;
        return new_location;
    }
} Location;



class Tile
{
    int number;
    Wormhole wormhole;
    list<Planet> planets;
    Anomaly anomaly;
    Location location;
    string race;

    int resources;
    int influence;

    public:
    Tile(int);
    Tile(int, string);
    Tile(int, list<Planet>, Wormhole, Anomaly);
    Tile(int, list<Planet>, string race);
    string get_description_string() const;
    int get_number();
    Wormhole get_wormhole();
    Anomaly get_anomaly();
    void set_location(Location);
    Location get_location();
    int get_resource_value();
    int get_influence_value();
    bool is_home_system();
};

int Tile::get_resource_value()
{
    return resources;
}

int Tile::get_influence_value()
{
    return influence;
}

int Tile::get_number() {
    return number;
}

Anomaly Tile::get_anomaly() {
    return anomaly;
}

Wormhole Tile::get_wormhole() {
    return wormhole;
}

void Tile::set_location(Location l) {
    location = l;
}

Location Tile::get_location() {
    return location;
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

bool Tile::is_home_system()
{
    return race.length();
}

std::ostream& operator<< (std::ostream &out, Tile const& tile) {
    out << tile.get_description_string();
    return out;
}

Tile::Tile(int n)
{
    number = n;
    race = "";
}

Tile::Tile(int n, string race1)
{
    number = n;
    race = race1;
}

Tile::Tile(int n, list<Planet> p, Wormhole w, Anomaly a)
{
    number = n;
    planets = p;
    wormhole = w;
    anomaly = a;
    race = "";

    resources = 0;
    influence = 0;
    for (auto planet : planets) {
        resources += planet.resources;
        influence += planet.influence;
    }
}

Tile::Tile(int n, list<Planet> p, string race1)
{
    number = n;
    planets = p;
    wormhole = NO_WORMHOLE;
    anomaly = NO_ANOMALY;
    race = race1;

    resources = 0;
    influence = 0;
    for (auto planet : planets) {
        resources += planet.resources;
        influence += planet.influence;
    }
}

typedef map<Tile*,map<Tile*, float>> double_tile_map;

class Galaxy
{
    list<Tile> tiles;
    Tile *grid[7][7]; // Locations of tiles
    Tile *mecatol;
    list<Tile*> home_systems;
    list<Tile*> movable_systems;
    map<Wormhole, list<Tile*>> wormhole_systems;
    Tile boundary_tile; // used for inaccesable locations in the grid

    void import_tiles(string tile_filename);
    void random_home_tiles(int n);
    void dummy_home_tiles(int n);
    void initialize_grid();
    void place_tile(Location location, Tile*);
    void swap_tiles(Tile *, Tile *);
    Tile* get_tile_at(Location location);
    list<Tile*> get_adjacent(Tile* t1);
    map<Tile*, float> distance_to_other_tiles(Tile* t1);
    void visit_all(Tile* t1, map<Tile*, float>& visited, float distance);
    double_tile_map calculate_stakes(double_tile_map distances);
    vector<pair<Tile*, Tile*>> make_swap_list();

    public:
    Galaxy(string tile_filename);
    void print_grid();
    float evaluate_grid();
    void optimize_grid();
    void write_json(string filename);
};

Galaxy::Galaxy(string tile_filename)
    : boundary_tile(0)
{
    import_tiles(tile_filename);
    //random_home_tiles(6);
    dummy_home_tiles(6);
    initialize_grid();

    //for (auto i : tiles) {
    //    cout << i << endl;
    //}
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
        Tile *added_tile = &tiles.back();
        movable_systems.push_back(added_tile);
        if (added_tile->get_wormhole()) {
            wormhole_systems[added_tile->get_wormhole()].push_back(added_tile);
        }
    }
    // Also home tiles
    tile_list = tile_json["home_tiles"];
    for (json::iterator it = tile_list.begin(); it != tile_list.end(); it++) {
        tiles.push_back(create_tile_from_json(it.value()));
        Tile *added_tile = &tiles.back();
        home_systems.push_back(added_tile);
    }
    
    // Save a pointer to mecatol rex
    tiles.push_back(create_tile_from_json(tile_json["mecatol"]));
    mecatol = &tiles.back();

    cerr << "Loaded " << tiles.size() << " tiles" << endl;
}

list<Tile*> get_shuffled_list(list<Tile*> l)
{
    vector<Tile *> to_shuffle;
    list<Tile *> ret;
    for (auto it : l) {
        to_shuffle.push_back(it);
    }
    random_shuffle(to_shuffle.begin(), to_shuffle.end());
    for (auto it : to_shuffle) {
        ret.push_back(it);
    }
    return ret;
}

void Galaxy::random_home_tiles(int n) {
    auto shuffled = get_shuffled_list(home_systems);
    auto it = shuffled.begin();
    home_systems.clear();
    list<Tile*> new_home_tiles;
    for (int i = 0; i < n; i++) {
        home_systems.push_back(*it);
        it++;
    }
}

void Galaxy::dummy_home_tiles(int n) {
    home_systems.clear();
    for (int i = 0; i < n; i++) {
        Tile new_tile = Tile(-i - 1, "Home System");
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
    movable_systems.clear();
    random_shuffle(random_tiles.begin(), random_tiles.end());

    for (int i = 0; i < 7;i++) {
        for (int j = 0; j < 7; j++) {
            if (not grid[i][j]) {
                place_tile({i, j}, random_tiles.back());
                movable_systems.push_back(random_tiles.back());
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

Tile* Galaxy::get_tile_at(Location l) {
    //TODO different size?
    if (l.i < 0 or l.i > 6 or l.j < 0 or l.j > 6) {
        return NULL;
    }
    Tile * tile = grid[l.i][l.j];
    if (tile == &boundary_tile) {
        return NULL;
    }
    return tile;
}

list<Tile*> Galaxy::get_adjacent(Tile *t1)
{
    list<Location> directions = {
        {0,1}, {1,1}, {1, 0}, {0, -1}, {-1, -1}, {-1, 0}
    };
    list<Tile*> adjacent;

    // Get tiles directly adjecent
    Location start_location = t1->get_location();
    for (auto it : directions) {
        Location new_location = start_location + it;
        Tile* potential_adjacent = get_tile_at(new_location);
        if (potential_adjacent) {
            adjacent.push_back(potential_adjacent);
        }
    }
    // Get connected wormholes
    if (t1->get_wormhole()) {
        for(Tile* it : wormhole_systems[t1->get_wormhole()]) {
            if (it != t1) {
                adjacent.push_back(it);
            }
        }
    }

    return adjacent;
};


void Galaxy::visit_all(Tile* t, map<Tile*, float>& visited, float distance)
{
    if (distance > 10) {
        return;
    }
   //cout << "distance " << distance << " at " << t << " " << t->get_description_string() << endl;
    
    float move_cost;
    // TODO: configure these?
    switch (t->get_anomaly()) {
        case NEBULA: move_cost = 2;
                     break;
        case ASTEROID_FIELD: move_cost = 1.5;
        case SUPERNOVA: return; // can't go through supernovas
        case GRAVITY_RIFT: move_cost = 1;
        default : move_cost = 1;
    }

    // don't travel through other home systems either
    if (t->is_home_system() and distance > 0) {
        return;
    }

    // If we didn't already visit, or our trip was shorter record distance and keep going
    if ((not visited.count(t)) or visited[t] > distance) {
        visited[t] = distance;
        //for(auto adjacent : get_adjacent(t)) {
        //    cout << " Will visit " << adjacent->get_description_string() << endl;
        //}
        for(auto adjacent : get_adjacent(t)) {
            visit_all(adjacent, visited, distance + move_cost);
        }
    }
}

map<Tile*, float> Galaxy::distance_to_other_tiles(Tile* t1) {
    map<Tile*, float> visited;
    visit_all(t1, visited, 0);
    return visited;
}


double_tile_map Galaxy::calculate_stakes(double_tile_map distances)
{
    double_tile_map stakes;
    for (auto t : movable_systems) {
        map<Tile*, float> stakes_in_system;
        for (auto hs : home_systems) {
            try {
                stakes_in_system[hs] = 1.0 / pow(distances[hs].at(t), 2);
            } catch (out_of_range) {
                // Systems like supernovas will not have any stake in them
                stakes_in_system[hs] = 0;
            }
        }
        float total_stake = 0;
        for (auto it : stakes_in_system) {
            total_stake += it.second;
        }
        if (total_stake == 0) {
            continue;
        }
        for (auto it : stakes_in_system) {
            stakes_in_system[it.first] /= total_stake;
        }
        stakes[t] = stakes_in_system;
    }
    return stakes;
}

typedef struct Scores
{
    map<Tile*, float> resource_share;
    map<Tile*, float> influence_share;
} Scores;

float average(list<float> l) 
{
    float sum = 0;
    for (auto it : l) {
        sum += it;
    }
    return sum / l.size();
}

float coefficient_of_variation(list<float> l) {
    float sum = 0;
    float avg = average(l);
    for (auto it : l) {
        sum += pow(it - avg, 2);
    }
    return sum / l.size() / avg;
}


float Galaxy::evaluate_grid() {
    float score = 0;
    
    map<Tile*, map<Tile*, float>> distances_from_home_systems;

    for (auto home_system : home_systems) {
        distances_from_home_systems[home_system] = distance_to_other_tiles(home_system);
    }
    double_tile_map stakes = calculate_stakes(distances_from_home_systems);

    //for (auto it1 : stakes) {
    //    cout << "Stakes in " << it1.first->get_description_string() << endl;
    //    for (auto it2 : it1.second) {
    //        cout << "\t" << it2.second << " " << it2.first->get_description_string() << endl;
    //    }
    //}

    Scores scores;

    float total_resources = 0;
    float total_influence = 0;
    list<float> resource_shares;
    list<float> influence_shares;
    for (auto home_system : home_systems) {
        float resource_share = 0;
        float influence_share = 0;
        for (auto tile : movable_systems) {
            resource_share += tile->get_resource_value() * stakes[tile][home_system];
            influence_share += tile->get_influence_value() * stakes[tile][home_system];
        }
        scores.resource_share[home_system] = resource_share;
        scores.influence_share[home_system] = influence_share;

        resource_shares.push_back(resource_share);
        influence_shares.push_back(influence_share);

        total_resources += resource_share;
        total_influence += influence_share;
    }

    //for (auto hs: home_systems) {
    //    printf("%2.1f %2.1f %s\n", scores.resource_share[hs], scores.influence_share[hs],
    //            hs->get_description_string().c_str());
    //}
    //printf("%2.1f %2.1f %s\n", total_resources, total_influence, "Totals");
    //printf("%0.3f %0.3f %s\n", coefficient_of_variation(resource_shares), 
    //        coefficient_of_variation(influence_shares), "CVs");

    return coefficient_of_variation(resource_shares) + coefficient_of_variation(influence_shares);
}

void Galaxy::swap_tiles(Tile* a, Tile* b)
{
    Location a_start = a->get_location();
    Location b_start = b->get_location();

    place_tile(a_start, b);
    place_tile(b_start, a);
}

vector<pair<Tile*, Tile*>> Galaxy::make_swap_list()
{
    vector<pair<Tile*, Tile*>> swap_list;
    for (auto t1 = movable_systems.begin(); t1 != movable_systems.end(); t1++) {
        auto t2 = t1;
        advance(t2, 1);
        for (; t2 != movable_systems.end(); t2++) {
            swap_list.push_back({*t1, *t2});
        }
    }
    random_shuffle(swap_list.begin(), swap_list.end());
    return swap_list;
}

void Galaxy::optimize_grid()
{
    float current_score = evaluate_grid();
    bool better_score_found = 0;

    int n_swaps = 0;
    int swaps_until_quit = 100;

    do {
        auto swaps = make_swap_list();

        n_swaps = 0;
        for (auto swap : swaps) {
            swap_tiles(swap.first, swap.second);
            float new_score = evaluate_grid();
            if (new_score < current_score) {
                better_score_found = true;
                current_score = new_score;
                printf("Swapping tiles %d & %d, new_score: %0.3f\n", 
                        swap.first->get_number(), swap.second->get_number(), current_score);
                //print_grid();
                break;
            } else {
                swap_tiles(swap.first, swap.second);
            }
            n_swaps++;
            if (n_swaps > swaps_until_quit) {
                break;
            }
        }
    } while (better_score_found and n_swaps < swaps_until_quit);
}

void Galaxy::write_json(string filename)
{
    json j;
    j["grid"] = json::array();
    for (int i = 0; i < 7; i++) {
        auto row = json::array();
        for (int j = 0; j < 7; j++) {
            row.push_back(grid[i][j]->get_number());
        }
        j["grid"].push_back(row);
    }
    
    ofstream galaxy_output_file;
    galaxy_output_file.open(filename);
    galaxy_output_file << j;
    galaxy_output_file.close();
}

int main() {

    srand(time(NULL));

    Galaxy galaxy("tiles.json");
    float score = galaxy.evaluate_grid();
    cout << "Score: " << score << endl;
    galaxy.optimize_grid();
    score = galaxy.evaluate_grid();
    cout << "Score: " << score << endl;
    galaxy.print_grid();
    galaxy.write_json("galaxy.json");

    return 0;
}
