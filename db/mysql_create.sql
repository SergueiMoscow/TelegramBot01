CREATE TABLE `photos` (
  `id` int(11) NOT NULL,
  `user` varchar(255) DEFAULT NULL,
  `added` varchar(255) DEFAULT NULL,
  `file` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `photos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `i_user` (`user`);

ALTER TABLE `photos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

CREATE TABLE `anekdot_user` (
  `id` int(11) NOT NULL,
  `user` varchar(255) DEFAULT NULL,
  `date` varchar(10) DEFAULT NULL,
  `category` varchar(1) DEFAULT NULL,
  `passed` int NOT NULL DEFAULT 0,
  `an_ids` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `anekdot_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_date` (`user`, `category`, `date`),
  ADD KEY `i_user` (`user`);

ALTER TABLE `anekdot_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

CREATE TABLE `anekdot` (
  `id` int NOT NULL,
  `date` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category` varchar(1) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `consecutive` int NOT NULL DEFAULT '0',
  `an_id` int NOT NULL DEFAULT '0',
  `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `anekdot`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `i_date` (`category`,`date`,`consecutive`);

ALTER TABLE `anekdot`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;
COMMIT;
