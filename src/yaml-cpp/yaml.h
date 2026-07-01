#pragma once

#include <cctype>
#include <cstddef>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

namespace YAML {

class Node {
 public:
  enum class Type { Null, Scalar, Map };

  Node() = default;

  Node& operator[](const std::string& key) {
    type_ = Type::Map;
    return map_[key];
  }

  const Node& operator[](const std::string& key) const {
    static Node empty;
    const auto iter = map_.find(key);
    if (iter == map_.end()) {
      return empty;
    }
    return iter->second;
  }

  template <typename T>
  T as() const;

  void setScalar(std::string value) {
    type_ = Type::Scalar;
    scalar_ = std::move(value);
  }

  void setMap() { type_ = Type::Map; }

 private:
  Type type_ = Type::Null;
  std::string scalar_;
  std::map<std::string, Node> map_;

  friend Node LoadFile(const std::string& path);
};

inline std::string trim(const std::string& value) {
  std::size_t start = 0;
  while (start < value.size() && std::isspace(static_cast<unsigned char>(value[start]))) {
    ++start;
  }
  std::size_t end = value.size();
  while (end > start && std::isspace(static_cast<unsigned char>(value[end - 1]))) {
    --end;
  }
  return value.substr(start, end - start);
}

inline std::string strip_comment(const std::string& value) {
  bool in_quote = false;
  char quote = '\0';
  for (std::size_t idx = 0; idx < value.size(); ++idx) {
    char ch = value[idx];
    if ((ch == '"' || ch == '\'') && (idx == 0 || value[idx - 1] != '\\')) {
      if (!in_quote) {
        in_quote = true;
        quote = ch;
      } else if (quote == ch) {
        in_quote = false;
      }
    }
    if (ch == '#' && !in_quote) {
      return value.substr(0, idx);
    }
  }
  return value;
}

inline int indent_width(const std::string& value) {
  int width = 0;
  for (char ch : value) {
    if (ch == ' ') {
      ++width;
    } else if (ch == '\t') {
      width += 2;
    } else {
      break;
    }
  }
  return width;
}

inline Node LoadFile(const std::string& path) {
  std::ifstream input(path);
  if (!input.is_open()) {
    throw std::runtime_error("Failed to open YAML file: " + path);
  }

  Node root;
  root.setMap();
  std::map<int, Node*> levels;
  levels[0] = &root;

  std::string line;
  while (std::getline(input, line)) {
    std::string no_comment = trim(strip_comment(line));
    if (no_comment.empty()) {
      continue;
    }

    int indent = indent_width(line);
    while (!levels.empty() && levels.rbegin()->first > indent) {
      levels.erase(std::prev(levels.end()));
    }
    Node* parent = levels.rbegin()->second;

    const std::size_t colon = no_comment.find(':');
    if (colon == std::string::npos) {
      continue;
    }

    std::string key = trim(no_comment.substr(0, colon));
    std::string value = trim(no_comment.substr(colon + 1));
    Node& child = (*parent)[key];
    if (value.empty()) {
      child.setMap();
      levels[indent + 2] = &child;
    } else {
      child.setScalar(value);
    }
  }

  return root;
}

template <>
inline std::string Node::as<std::string>() const {
  return scalar_;
}

template <>
inline int Node::as<int>() const {
  return std::stoi(scalar_);
}

template <>
inline double Node::as<double>() const {
  return std::stod(scalar_);
}

template <>
inline bool Node::as<bool>() const {
  if (scalar_ == "true" || scalar_ == "on" || scalar_ == "yes" || scalar_ == "1") {
    return true;
  }
  if (scalar_ == "false" || scalar_ == "off" || scalar_ == "no" || scalar_ == "0") {
    return false;
  }
  throw std::runtime_error("Invalid YAML boolean: " + scalar_);
}

}  // namespace YAML
