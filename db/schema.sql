-- Dimensions
CREATE TABLE dbo.dim_competition (
  comp_id       INT        NOT NULL PRIMARY KEY,
  comp_name     NVARCHAR(100) NOT NULL,
  comp_type     NVARCHAR(50)  NULL,
  area_name     NVARCHAR(100) NULL,
  code          NVARCHAR(10)  NULL,
  last_updated  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.dim_team (
  team_id      INT           NOT NULL PRIMARY KEY,
  team_name    NVARCHAR(120) NOT NULL,
  tla          NVARCHAR(10)  NULL,
  country      NVARCHAR(80)  NULL,
  founded      INT           NULL,
  last_updated DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.dim_date (
  date_id      DATE          NOT NULL PRIMARY KEY,
  yr           SMALLINT      NOT NULL,
  mn           TINYINT       NOT NULL,
  dy           TINYINT       NOT NULL,
  wk           TINYINT       NOT NULL
);

-- Facts
CREATE TABLE dbo.fact_match (
  match_id        INT           NOT NULL PRIMARY KEY,
  comp_id         INT           NOT NULL,
  season          INT           NOT NULL,
  utc_date        DATETIME2     NOT NULL,
  status          NVARCHAR(32)  NOT NULL, -- SCHEDULED/LIVE/FINISHED
  round           NVARCHAR(64)  NULL,
  home_team_id    INT           NOT NULL,
  away_team_id    INT           NOT NULL,
  ft_home_goals   SMALLINT      NULL,
  ft_away_goals   SMALLINT      NULL,
  winner          NVARCHAR(32)  NULL,
  last_updated    DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
  CONSTRAINT FK_match_comp FOREIGN KEY (comp_id) REFERENCES dbo.dim_competition(comp_id),
  CONSTRAINT FK_match_home FOREIGN KEY (home_team_id) REFERENCES dbo.dim_team(team_id),
  CONSTRAINT FK_match_away FOREIGN KEY (away_team_id) REFERENCES dbo.dim_team(team_id)
);

CREATE TABLE dbo.fact_standing (
  comp_id       INT          NOT NULL,
  season        INT          NOT NULL,
  team_id       INT          NOT NULL,
  position      INT          NOT NULL,
  points        INT          NOT NULL,
  played        INT          NOT NULL,
  won           INT          NOT NULL,
  draw          INT          NOT NULL,
  lost          INT          NOT NULL,
  goals_for     INT          NOT NULL,
  goals_against INT          NOT NULL,
  last_updated  DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME(),
  CONSTRAINT PK_fact_standing PRIMARY KEY (comp_id, season, team_id),
  CONSTRAINT FK_stand_comp FOREIGN KEY (comp_id) REFERENCES dbo.dim_competition(comp_id),
  CONSTRAINT FK_stand_team FOREIGN KEY (team_id) REFERENCES dbo.dim_team(team_id)
);