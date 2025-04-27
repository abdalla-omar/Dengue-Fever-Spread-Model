#ifndef DENGUE_CELL_HPP
#define DENGUE_CELL_HPP

#include <cadmium/modeling/celldevs/asymm/cell.hpp>
#include <nlohmann/json.hpp>
#include <iostream>

using namespace cadmium::celldevs;
using namespace std;

// Your SEIR + any vector fields
struct DengueState {
    double susceptible{0}, exposed{0}, infectious{0}, recovered{0};
};

// Logging & comparison
inline ostream& operator<<(ostream& os, DengueState const& s) {
    return os << "<S="<<s.susceptible
              <<",E="<<s.exposed
              <<",I="<<s.infectious
              <<",R="<<s.recovered<<">";
}
inline bool operator!=(DengueState const& a, DengueState const& b) {
    return a.susceptible!=b.susceptible
        || a.exposed   !=b.exposed
        || a.infectious!=b.infectious
        || a.recovered !=b.recovered;
}

// JSON→state
inline void from_json(nlohmann::json const& j, DengueState& s) {
    j.at("susceptible").get_to(s.susceptible);
    j.at("exposed")    .get_to(s.exposed);
    j.at("infectious") .get_to(s.infectious);
    j.at("recovered")  .get_to(s.recovered);
}

// Your asymmetric cell: IDs are strings
class DengueCell : public AsymmCell<DengueState,double> {
public:
  DengueCell(const std::string& id,
	const std::shared_ptr<const AsymmCellConfig<DengueState,double>>& cfg)
: AsymmCell<DengueState,double>(id,cfg) {}


  // exact override signature from AsymmCell:
  [[nodiscard]] DengueState localComputation(
    DengueState state,
    const unordered_map<string,NeighborData<DengueState,double>>& nbrs,
    const PortSet& x) const override
  {
    // TODO: compute new SEIR using:
    //   - state.* fields
    //   - cfg->config["beta"],["sigma"],["gamma"]
    //   - each neighbor's nbrs[neighborID].state->infectious * nbrs[neighborID].weight
    return state;
  }

  // same delay as your default
  [[nodiscard]] double outputDelay(DengueState const&) const override {
    return 1.0;
  }
};

#endif // DENGUE_CELL_HPP
