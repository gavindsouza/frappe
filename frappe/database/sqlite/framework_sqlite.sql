PRAGMA synchronous = OFF;
PRAGMA journal_mode = MEMORY;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS `tabDocField`;
CREATE TABLE `tabDocField` (
  `name` varchar(255) NOT NULL
,  `creation` datetime(6) DEFAULT NULL
,  `modified` datetime(6) DEFAULT NULL
,  `modified_by` varchar(255) DEFAULT NULL
,  `owner` varchar(255) DEFAULT NULL
,  `docstatus` integer NOT NULL DEFAULT 0
,  `parent` varchar(255) DEFAULT NULL
,  `parentfield` varchar(255) DEFAULT NULL
,  `parenttype` varchar(255) DEFAULT NULL
,  `idx` integer NOT NULL DEFAULT 0
,  `fieldname` varchar(255) DEFAULT NULL
,  `label` varchar(255) DEFAULT NULL
,  `oldfieldname` varchar(255) DEFAULT NULL
,  `fieldtype` varchar(255) DEFAULT NULL
,  `oldfieldtype` varchar(255) DEFAULT NULL
,  `options` text
,  `search_index` integer NOT NULL DEFAULT 0
,  `hidden` integer NOT NULL DEFAULT 0
,  `set_only_once` integer NOT NULL DEFAULT 0
,  `allow_in_quick_entry` integer NOT NULL DEFAULT 0
,  `print_hide` integer NOT NULL DEFAULT 0
,  `report_hide` integer NOT NULL DEFAULT 0
,  `reqd` integer NOT NULL DEFAULT 0
,  `bold` integer NOT NULL DEFAULT 0
,  `in_global_search` integer NOT NULL DEFAULT 0
,  `collapsible` integer NOT NULL DEFAULT 0
,  `unique` integer NOT NULL DEFAULT 0
,  `no_copy` integer NOT NULL DEFAULT 0
,  `allow_on_submit` integer NOT NULL DEFAULT 0
,  `show_preview_popup` integer NOT NULL DEFAULT 0
,  `trigger` varchar(255) DEFAULT NULL
,  `collapsible_depends_on` text
,  `mandatory_depends_on` text
,  `read_only_depends_on` text
,  `depends_on` text
,  `permlevel` integer NOT NULL DEFAULT 0
,  `ignore_user_permissions` integer NOT NULL DEFAULT 0
,  `width` varchar(255) DEFAULT NULL
,  `print_width` varchar(255) DEFAULT NULL
,  `columns` integer NOT NULL DEFAULT 0
,  `default` text
,  `description` text
,  `in_list_view` integer NOT NULL DEFAULT 0
,  `fetch_if_empty` integer NOT NULL DEFAULT 0
,  `in_filter` integer NOT NULL DEFAULT 0
,  `remember_last_selected_value` integer NOT NULL DEFAULT 0
,  `ignore_xss_filter` integer NOT NULL DEFAULT 0
,  `print_hide_if_no_value` integer NOT NULL DEFAULT 0
,  `allow_bulk_edit` integer NOT NULL DEFAULT 0
,  `in_standard_filter` integer NOT NULL DEFAULT 0
,  `in_preview` integer NOT NULL DEFAULT 0
,  `read_only` integer NOT NULL DEFAULT 0
,  `precision` varchar(255) DEFAULT NULL
,  `length` integer NOT NULL DEFAULT 0
,  `translatable` integer NOT NULL DEFAULT 0
,  `hide_border` integer NOT NULL DEFAULT 0
,  `hide_days` integer NOT NULL DEFAULT 0
,  `hide_seconds` integer NOT NULL DEFAULT 0
,  PRIMARY KEY (`name`)
);

DROP TABLE IF EXISTS `tabDocPerm`;
CREATE TABLE `tabDocPerm` (
  `name` varchar(255) NOT NULL
,  `creation` datetime(6) DEFAULT NULL
,  `modified` datetime(6) DEFAULT NULL
,  `modified_by` varchar(255) DEFAULT NULL
,  `owner` varchar(255) DEFAULT NULL
,  `docstatus` integer NOT NULL DEFAULT 0
,  `parent` varchar(255) DEFAULT NULL
,  `parentfield` varchar(255) DEFAULT NULL
,  `parenttype` varchar(255) DEFAULT NULL
,  `idx` integer NOT NULL DEFAULT 0
,  `permlevel` integer DEFAULT '0'
,  `role` varchar(255) DEFAULT NULL
,  `match` varchar(255) DEFAULT NULL
,  `read` integer NOT NULL DEFAULT 1
,  `write` integer NOT NULL DEFAULT 1
,  `create` integer NOT NULL DEFAULT 1
,  `submit` integer NOT NULL DEFAULT 0
,  `cancel` integer NOT NULL DEFAULT 0
,  `delete` integer NOT NULL DEFAULT 1
,  `amend` integer NOT NULL DEFAULT 0
,  `report` integer NOT NULL DEFAULT 1
,  `export` integer NOT NULL DEFAULT 1
,  `import` integer NOT NULL DEFAULT 0
,  `share` integer NOT NULL DEFAULT 1
,  `print` integer NOT NULL DEFAULT 1
,  `email` integer NOT NULL DEFAULT 1
,  PRIMARY KEY (`name`)
);

DROP TABLE IF EXISTS `tabDocType Action`;
CREATE TABLE `tabDocType Action` (
  `name` varchar(140) NOT NULL
,  `creation` datetime(6) DEFAULT NULL
,  `modified` datetime(6) DEFAULT NULL
,  `modified_by` varchar(140) DEFAULT NULL
,  `owner` varchar(140) DEFAULT NULL
,  `docstatus` integer NOT NULL DEFAULT 0
,  `parent` varchar(140) DEFAULT NULL
,  `parentfield` varchar(140) DEFAULT NULL
,  `parenttype` varchar(140) DEFAULT NULL
,  `idx` integer NOT NULL DEFAULT 0
,  `label` varchar(140) DEFAULT NULL
,  `group` varchar(140) DEFAULT NULL
,  `action_type` varchar(140) DEFAULT NULL
,  `action` text DEFAULT NULL
,  PRIMARY KEY (`name`)
);

DROP TABLE IF EXISTS `tabDocType Link`;
CREATE TABLE `tabDocType Link` (
  `name` varchar(140) NOT NULL
,  `creation` datetime(6) DEFAULT NULL
,  `modified` datetime(6) DEFAULT NULL
,  `modified_by` varchar(140) DEFAULT NULL
,  `owner` varchar(140) DEFAULT NULL
,  `docstatus` integer NOT NULL DEFAULT 0
,  `parent` varchar(140) DEFAULT NULL
,  `parentfield` varchar(140) DEFAULT NULL
,  `parenttype` varchar(140) DEFAULT NULL
,  `idx` integer NOT NULL DEFAULT 0
,  `group` varchar(140) DEFAULT NULL
,  `link_doctype` varchar(140) DEFAULT NULL
,  `link_fieldname` varchar(140) DEFAULT NULL
,  PRIMARY KEY (`name`)
);

DROP TABLE IF EXISTS `tabDocType`;
CREATE TABLE `tabDocType` (
  `name` varchar(255) NOT NULL
,  `creation` datetime(6) DEFAULT NULL
,  `modified` datetime(6) DEFAULT NULL
,  `modified_by` varchar(255) DEFAULT NULL
,  `owner` varchar(255) DEFAULT NULL
,  `docstatus` integer NOT NULL DEFAULT 0
,  `parent` varchar(255) DEFAULT NULL
,  `parentfield` varchar(255) DEFAULT NULL
,  `parenttype` varchar(255) DEFAULT NULL
,  `idx` integer NOT NULL DEFAULT 0
,  `search_fields` varchar(255) DEFAULT NULL
,  `issingle` integer NOT NULL DEFAULT 0
,  `is_tree` integer NOT NULL DEFAULT 0
,  `istable` integer NOT NULL DEFAULT 0
,  `editable_grid` integer NOT NULL DEFAULT 1
,  `track_changes` integer NOT NULL DEFAULT 0
,  `module` varchar(255) DEFAULT NULL
,  `restrict_to_domain` varchar(255) DEFAULT NULL
,  `app` varchar(255) DEFAULT NULL
,  `autoname` varchar(255) DEFAULT NULL
,  `name_case` varchar(255) DEFAULT NULL
,  `title_field` varchar(255) DEFAULT NULL
,  `image_field` varchar(255) DEFAULT NULL
,  `timeline_field` varchar(255) DEFAULT NULL
,  `sort_field` varchar(255) DEFAULT NULL
,  `sort_order` varchar(255) DEFAULT NULL
,  `description` text
,  `colour` varchar(255) DEFAULT NULL
,  `read_only` integer NOT NULL DEFAULT 0
,  `in_create` integer NOT NULL DEFAULT 0
,  `menu_index` integer DEFAULT NULL
,  `parent_node` varchar(255) DEFAULT NULL
,  `smallicon` varchar(255) DEFAULT NULL
,  `allow_copy` integer NOT NULL DEFAULT 0
,  `allow_rename` integer NOT NULL DEFAULT 0
,  `allow_import` integer NOT NULL DEFAULT 0
,  `hide_toolbar` integer NOT NULL DEFAULT 0
,  `track_seen` integer NOT NULL DEFAULT 0
,  `max_attachments` integer NOT NULL DEFAULT 0
,  `print_outline` varchar(255) DEFAULT NULL
,  `document_type` varchar(255) DEFAULT NULL
,  `icon` varchar(255) DEFAULT NULL
,  `color` varchar(255) DEFAULT NULL
,  `tag_fields` varchar(255) DEFAULT NULL
,  `subject` varchar(255) DEFAULT NULL
,  `_last_update` varchar(32) DEFAULT NULL
,  `engine` varchar(20) DEFAULT 'InnoDB'
,  `default_print_format` varchar(255) DEFAULT NULL
,  `is_submittable` integer NOT NULL DEFAULT 0
,  `show_name_in_global_search` integer NOT NULL DEFAULT 0
,  `_user_tags` varchar(255) DEFAULT NULL
,  `custom` integer NOT NULL DEFAULT 0
,  `beta` integer NOT NULL DEFAULT 0
,  `has_web_view` integer NOT NULL DEFAULT 0
,  `allow_guest_to_view` integer NOT NULL DEFAULT 0
,  `route` varchar(255) DEFAULT NULL
,  `is_published_field` varchar(255) DEFAULT NULL
,  `website_search_field` varchar(255) DEFAULT NULL
,  `email_append_to` integer NOT NULL DEFAULT 0
,  `subject_field` varchar(255) DEFAULT NULL
,  `sender_field` varchar(255) DEFAULT NULL
,  PRIMARY KEY (`name`)
);

DROP TABLE IF EXISTS `tabSeries`;
CREATE TABLE `tabSeries` (
  `name` varchar(100)
,  `current` integer NOT NULL DEFAULT 0
,  PRIMARY KEY(`name`)
);

DROP TABLE IF EXISTS `tabSessions`;
CREATE TABLE `tabSessions` (
  `user` varchar(255) DEFAULT NULL
,  `sid` varchar(255) DEFAULT NULL
,  `sessiondata` longtext
,  `ipaddress` varchar(16) DEFAULT NULL
,  `lastupdate` datetime(6) DEFAULT NULL
,  `device` varchar(255) DEFAULT 'desktop'
,  `status` varchar(20) DEFAULT NULL
);

DROP TABLE IF EXISTS `tabSingles`;
CREATE TABLE `tabSingles` (
  `doctype` varchar(255) DEFAULT NULL
,  `field` varchar(255) DEFAULT NULL
,  `value` text
);

DROP TABLE IF EXISTS `__Auth`;
CREATE TABLE `__Auth` (
	`doctype` VARCHAR(140) NOT NULL,
	`name` VARCHAR(255) NOT NULL,
	`fieldname` VARCHAR(140) NOT NULL,
	`password` TEXT NOT NULL,
	`encrypted` INT(1) NOT NULL DEFAULT 0,
	PRIMARY KEY (`doctype`, `name`, `fieldname`)
);

DROP TABLE IF EXISTS `tabFile`;
CREATE TABLE `tabFile` (
  `name` varchar(255) NOT NULL
,  `creation` datetime(6) DEFAULT NULL
,  `modified` datetime(6) DEFAULT NULL
,  `modified_by` varchar(255) DEFAULT NULL
,  `owner` varchar(255) DEFAULT NULL
,  `docstatus` integer NOT NULL DEFAULT 0
,  `parent` varchar(255) DEFAULT NULL
,  `parentfield` varchar(255) DEFAULT NULL
,  `parenttype` varchar(255) DEFAULT NULL
,  `idx` integer NOT NULL DEFAULT 0
,  `file_name` varchar(255) DEFAULT NULL
,  `file_url` varchar(255) DEFAULT NULL
,  `module` varchar(255) DEFAULT NULL
,  `attached_to_name` varchar(255) DEFAULT NULL
,  `file_size` integer NOT NULL DEFAULT 0
,  `attached_to_doctype` varchar(255) DEFAULT NULL
,  PRIMARY KEY (`name`)
);


DROP TABLE IF EXISTS `tabDefaultValue`;
CREATE TABLE `tabDefaultValue` (
  `name` varchar(255) NOT NULL
,  `creation` datetime(6) DEFAULT NULL
,  `modified` datetime(6) DEFAULT NULL
,  `modified_by` varchar(255) DEFAULT NULL
,  `owner` varchar(255) DEFAULT NULL
,  `docstatus` integer NOT NULL DEFAULT 0
,  `parent` varchar(255) DEFAULT NULL
,  `parentfield` varchar(255) DEFAULT NULL
,  `parenttype` varchar(255) DEFAULT NULL
,  `idx` integer NOT NULL DEFAULT 0
,  `defvalue` text
,  `defkey` varchar(255) DEFAULT NULL
,  PRIMARY KEY (`name`)
);

CREATE INDEX "idx_tabDocType Link_parent" ON "tabDocType Link" (`parent`);
CREATE INDEX "idx_tabDocType Link_modified" ON "tabDocType Link" (`modified`);
CREATE INDEX "idx_tabDocPerm_parent" ON "tabDocPerm" (`parent`);
CREATE INDEX "idx_tabSessions_sid" ON "tabSessions" (`sid`);
CREATE INDEX "idx_tabDocType Action_parent" ON "tabDocType Action" (`parent`);
CREATE INDEX "idx_tabDocType Action_modified" ON "tabDocType Action" (`modified`);
CREATE INDEX "idx_tabDocType_parent" ON "tabDocType" (`parent`);
CREATE INDEX "idx_tabFile_parent" ON "tabFile" (`parent`);
CREATE INDEX "idx_tabFile_attached_to_name" ON "tabFile" (`attached_to_name`);
CREATE INDEX "idx_tabFile_attached_to_doctype" ON "tabFile" (`attached_to_doctype`);
CREATE INDEX "idx_tabDocField_parent" ON "tabDocField" (`parent`);
CREATE INDEX "idx_tabDocField_label" ON "tabDocField" (`label`);
CREATE INDEX "idx_tabDocField_fieldtype" ON "tabDocField" (`fieldtype`);
CREATE INDEX "idx_tabDocField_fieldname" ON "tabDocField" (`fieldname`);
CREATE INDEX "idx_tabSingles_singles_doctype_field_index" ON "tabSingles" (`doctype`, `field`);
CREATE INDEX "idx_tabDefaultValue_parent" ON "tabDefaultValue" (`parent`);
CREATE INDEX "idx_tabDefaultValue_defaultvalue_parent_defkey_index" ON "tabDefaultValue" (`parent`,`defkey`);
END TRANSACTION;
