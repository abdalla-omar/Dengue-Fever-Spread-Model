#ifndef DENGUE_CELL_HPP
#define DENGUE_CELL_HPP

#include <cadmium/modeling/celldevs/asymm/cell.hpp>
#include "dengue_state.hpp"
#include <cmath>

using namespace cadmium::celldevs;

/// A Dengue‐SEIR cell under the new AsymmCell API
class DengueCell : public AsymmCell<DengueState, double> {
public:
  DengueCell(const std::string& id,
             const std::shared_ptr<const AsymmCellConfig<DengueState,double>>& config)
    : AsymmCell<DengueState,double>(id, config)
  {
    // pull your parameters out of the JSON “config” block
    config->rawCellConfig.at("beta").get_to(beta);
    config->rawCellConfig.at("sigma").get_to(incubationRate);
    config->rawCellConfig.at("gamma").get_to(recoveryRate);
  }

  // —— This exactly matches the pure-virtual in the base class:
  DengueState localComputation(
    DengueState state,
    const std::unordered_map<std::string, NeighborData<DengueState,double>>& nb
  ) const override {
    // 1) force of infection from neighbors
    double force = 0.0;
    for (auto const& [nid, nd] : nb) {
      force += nd.state->I * nd.vicinity;
    }

    // 2) transitions
    int newE = std::min(state.S, int(beta * force));
    int newI = int(incubationRate * state.E);
    int newR = int(recoveryRate   * state.I);

    state.S -= newE;
    state.E += newE - newI;
    state.I += newI - newR;
    state.R += newR;

    return state;
  }

  // —— Also matches the signature in the base class:
  double outputDelay(const DengueState&) const override {
    // one day per update (or whatever time unit)
    return 1.0;
  }

private:
  double beta;             // transmission rate
  double incubationRate;   // E→I
  double recoveryRate;     // I→R
};

#endif // DENGUE_CELL_HPP
