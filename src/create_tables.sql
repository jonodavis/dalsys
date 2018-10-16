CREATE TABLE map (
  map_id INT, 
  name VARCHAR(50), 
  filepath VARCHAR(100), 
  PRIMARY KEY(name)
);

CREATE TABLE drone (
  drone_id INT, 
  name VARCHAR(50), 
  class_type INT, 
  rescue BOOLEAN, 
  operator_id INT, 
  map_id VARCHAR(50), 
  PRIMARY KEY(drone_id),
  FOREIGN KEY(map_id) REFERENCES map(name),
  FOREIGN KEY(operator_id) REFERENCES operator(operator_id)
);


CREATE TABLE operator (
  operator_id INT, 
  first_name VARCHAR(50), 
  family_name VARCHAR(50), 
  date_of_birth DATE, 
  drone_license INT, 
  rescue_endorsement BOOLEAN, 
  operations INT, 
  drone_id INT, 
  PRIMARY KEY(operator_id),
  FOREIGN KEY(drone_id) REFERENCES drone(drone_id)
);