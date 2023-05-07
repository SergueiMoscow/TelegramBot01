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
