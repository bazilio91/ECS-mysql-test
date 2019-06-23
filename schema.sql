CREATE DATABASE IF NOT EXISTS `test` /*!40100 DEFAULT CHARACTER SET utf8 */;

CREATE TABLE `PlayerData`
(
    `id`            int(11)      NOT NULL,
    `name`          varchar(255) NOT NULL,
    `clan`          int(10) unsigned      DEFAULT NULL,
    `created_at`    timestamp    NOT NULL DEFAULT current_timestamp(),
    `last_login`    timestamp    NULL     DEFAULT NULL,
    `password_hash` varchar(255)          DEFAULT NULL,
    `salt`          varchar(255)          DEFAULT NULL,
    `kills`         int(10) unsigned      DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `PlayerData_name_uindex` (`name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

CREATE TABLE `Container`
(
    `id`    int(11) NOT NULL,
    `owner` int(11) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `Container_PlayerData_id_fk` (`owner`),
    CONSTRAINT `Container_PlayerData_id_fk` FOREIGN KEY (`owner`) REFERENCES `PlayerData` (`id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

CREATE TABLE `Item`
(
    `id`        int(11) NOT NULL,
    `container` int(11)          DEFAULT NULL,
    `owner`     int(11)          DEFAULT NULL,
    `use_count` int(10) unsigned DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `Item_Container_id_fk` (`container`),
    KEY `Item_Container_owner_fk` (`owner`),
    CONSTRAINT `Item_Container_id_fk` FOREIGN KEY (`container`) REFERENCES `Container` (`id`),
    CONSTRAINT `Item_Container_owner_fk` FOREIGN KEY (`owner`) REFERENCES `Container` (`owner`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

CREATE TABLE `LocationHistory`
(
    `id`          int(11)   NOT NULL,
    `location_id` int(11)   NOT NULL,
    `date`        timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    UNIQUE KEY `LocationHistory_id_location_id_uindex` (`id`, `location_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;


CREATE TABLE `Position`
(
    `id`          int(11) DEFAULT NULL,
    `x`           float   DEFAULT NULL,
    `y`           float   DEFAULT NULL,
    `location_id` int(11) NOT NULL,
    PRIMARY KEY (`location_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8
