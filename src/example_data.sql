INSERT INTO operator () VALUES(
  0, 
  'Alex', 
  'Anderson', 
  '1990-02-05', 
  1, 
  False, 
  0, 
  NULL
);

INSERT INTO operator () VALUES(
  1,
  'Bobby',
  'Brown',
  '1989-03-06',
  1,
  False,
  4,
  NULL
);

INSERT INTO operator () VALUES(
  2,
  'Charlie',
  'Crock',
  '1984-12-25',
  2,
  False,
  10,
  NULL
);

INSERT INTO operator () VALUES(
  3,
  'David',
  'Davidson',
  '1998-04-01',
  2,
  True,
  21,
  NULL
);

INSERT INTO map () VALUES(
  0,
  'Abel Tasman',
  'map_abel_tasman_3.gif'
);

INSERT INTO map () VALUES(
  1,
  'Ruatiti',
  'map_ruatiti.gif'
);

INSERT INTO drone () VALUES(
  1,
  'Class One Search Drone',
  1,
  False,
  NULL,
  'Ruatiti'
);

INSERT INTO drone () VALUES(
  2,
  'Class Two Search Drone',
  2,
  False,
  NULL,
  'Ruatiti'
);

INSERT INTO drone () VALUES(
  3,
  'The Rescue Drone',
  1,
  True,
  NULL,
  'Ruatiti'
);

INSERT INTO drone () VALUES(
  4,
  'The Rescue Drone With Operator and Map',
  1,
  True,
  3,
  'Ruatiti'
);

INSERT INTO drone () VALUES(
  5,
  'The Search Drone With Operator and Map',
  1,
  False,
  1,
  'Ruatiti'
);