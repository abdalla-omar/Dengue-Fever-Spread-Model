#ifndef DENGUE_CELL_HPP
#define DENGUE_CELL_HPP

#include <cadmium/modeling/celldevs/asymm/cell.hpp>
#include "dengue_state.hpp"
#include <algorithm> // for std::min

using namespace cadmium::celldevs;

/// SEIR‐type cell for Dengue: no need to override internalTransition/externalTransition,
/// just implement tau (localComputation) and outputDelay.
class DengueCell : public AsymmCell<DengueState,double> {
public:
  DengueCell(const std::string& id,
             const std::shared_ptr<const AsymmCellConfig<DengueState,double>>& config)
    : AsymmCell<DengueState,double>(id, config)
  {
    // read your model parameters from JSON “config” block
    // JSON keys must match your config file (here: "beta0", "sigma", "gamma")
    config->rawCellConfig.at("beta").get_to(beta0_);
    config->rawCellConfig.at("sigma").get_to(sigma_rate_);
    config->rawCellConfig.at("gamma").get_to(gamma_rate_);
  }

  /// τ: given current state & neighborhood, compute next state
  DengueState localComputation(
    DengueState state,
    const std::unordered_map<std::string,NeighborData<DengueState,double>>& nb
  ) const override {
    // 1) force of infection from neighbors
    double force = 0.0;
    for (auto const& [nid, nd] : nb) {
      force += nd.state->I * nd.vicinity;
    }
    // 2) new exposures (fractional)
    double newE = std::min(state.S, beta0_ * force);
    // 3) E→I and I→R transitions
    double newI = sigma_rate_ * state.E;
    double newR = gamma_rate_ * state.I;

    // update compartments
    state.S -= newE;
    state.E += newE - newI;
    state.I += newI - newR;
    state.R += newR;
    return state;
  }

  /// one time‐unit per update (e.g., daily)
  double outputDelay(const DengueState&) const override {
    return 1.0;
  }

private:
  double beta0_;       // baseline transmission rate
  double sigma_rate_;  // incubation → infectious
  double gamma_rate_;  // recovery rate
};

#endif // DENGUE_CELL_HPP
