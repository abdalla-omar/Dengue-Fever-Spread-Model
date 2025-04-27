#ifndef DENGUE_CELL_HPP
#define DENGUE_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>   
#include <nlohmann/json.hpp>
#include <iostream>

using namespace cadmium::celldevs;  // GridCell lives here
using namespace std;

struct DengueState {
    double susceptible{1.0}, exposed{0.0}, infectious{0.0}, recovered{0.0};
};

inline ostream& operator<<(ostream& os, const DengueState& s) {
    os << "<S="<<s.susceptible
       <<",E="<<s.exposed
       <<",I="<<s.infectious
       <<",R="<<s.recovered<<">";
    return os;
}

inline bool operator!=(const DengueState& a, const DengueState& b) {
    return a.susceptible!=b.susceptible
        || a.exposed!=b.exposed
        || a.infectious!=b.infectious
        || a.recovered!=b.recovered;
}

inline void from_json(const nlohmann::json& j, DengueState& s) {
    j.at("susceptible").get_to(s.susceptible);
    j.at("exposed")    .get_to(s.exposed);
    j.at("infectious") .get_to(s.infectious);
    j.at("recovered")  .get_to(s.recovered);
}

// Inherit from GridCell (not AsymmCell)
class DengueCell : public GridCell<DengueState, double> {
public:
    DengueCell(const vector<int>& id,
               const shared_ptr<const GridCellConfig<DengueState,double>>& cfg)
      : GridCell<DengueState,double>(id, cfg) {}

    // matches GridCell’s signature exactly
    [[nodiscard]] DengueState localComputation(
        DengueState state,
        const unordered_map<vector<int>,NeighborData<DengueState,double>>& neigh
    ) const override {
        // TODO: implement S→E, E→I, I→R, vector pressure, etc.
        return state;
    }

    [[nodiscard]] double outputDelay(const DengueState&) const override {
        return 1.0;
    }
};

#endif // DENGUE_CELL_HPP
