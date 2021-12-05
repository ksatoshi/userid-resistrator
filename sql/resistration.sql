CREATE TABLE `resistration` (
	`user_id` INT(10) UNSIGNED NOT NULL,
	`area_id` INT(10) UNSIGNED NOT NULL,
	INDEX `FK__area` (`area_id`) USING BTREE,
	INDEX `FK__user` (`user_id`) USING BTREE,
	CONSTRAINT `FK__area` FOREIGN KEY (`area_id`) REFERENCES `hakodate_a05`.`area` (`ID`) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT `FK__user` FOREIGN KEY (`user_id`) REFERENCES `hakodate_a05`.`user` (`ID`) ON UPDATE CASCADE ON DELETE CASCADE
)
COLLATE='utf8mb3_general_ci'
ENGINE=InnoDB
;
