#ifndef DENGUE_STATE_HPP
#define DENGUE_STATE_HPP

#include <iostream>
#include <nlohmann/json.hpp>

/// SEIR state: counts of Susceptible, Exposed, Infectious, Recovered.
struct DengueState {
    int S, E, I, R;
    DengueState() : S(0), E(0), I(0), R(0) {}
};

/// Two states are “!=” if any compartment differs.
inline bool operator!=(const DengueState& a, const DengueState& b) {
    return a.S != b.S || a.E != b.E || a.I != b.I || a.R != b.R;
}

/// Log as “<S,E,I,R>”
inline std::ostream& operator<<(std::ostream& os, const DengueState& s) {
    os << "<" << s.S << "," << s.E << "," << s.I << "," << s.R << ">";
    return os;
}

/// Initialize from JSON object:
///   { "S":…, "E":…, "I":…, "R":… }
inline void from_json(const nlohmann::json& j, DengueState& s) {
    j.at("S").get_to(s.S);
    j.at("E").get_to(s.E);
    j.at("I").get_to(s.I);
    j.at("R").get_to(s.R);
}

#endif // DENGUE_STATE_HPP
