const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const rollup = require('rollup');
const { execSync } = require('child_process');
const log = console.log; // eslint-disable-line

const {
	get_build_json,
	get_app_path,
	apps_list,
	run_serially,
	assets_path,
	sites_path
} = require('./rollup.utils');

const {
	get_options_for
} = require('./config');

let memory_limit = '';
let limiter = '--max_old_space_size=';
const build_for_app = process.argv[2] === '--app' ? process.argv[3] : null;

for (let flag of process.argv) {
	 memory_limit = flag.startsWith(limiter) ? flag : memory_limit;
}

show_production_message();
ensure_js_css_dirs();
concatenate_files();
create_build_file();

if (build_for_app) {
	build_assets_for_app(build_for_app)
		.then(() => {
			run_build_command_for_app(build_for_app);
		})
} else {
	build_assets_for_all_apps()
		.then(() => {
			run_build_command_for_apps()
		});
}


function build_assets_for_all_apps() {
	return run_serially(
		apps_list.map(app => () => build_assets(app))
	);
}

function build_assets_for_app(app) {
	return build_assets(app)
}

function build_assets(app) {
	if (global.gc) {global.gc();}
	const options = get_options_for(app);
	if (!options.length) return Promise.resolve();
	log(chalk.yellow(`\nBuilding ${app} assets...\n`));

	const promises = options.map(({ inputOptions, outputOptions, output_file}) => {
		return build(inputOptions, outputOptions)
			.then(() => {
				log(`${chalk.green('✔')} Built ${output_file}`);
			});
	});

	const start = Date.now();
	return Promise.all(promises)
		.then(() => {
			const time = Date.now() - start;
			log(chalk.green(`✨  Done in ${time / 1000}s`));
		});
}

function build(inputOptions, outputOptions) {
	return rollup.rollup(inputOptions)
		.then(bundle => bundle.write(outputOptions))
		.catch(err => {
			log(chalk.red(err));
			// Kill process to fail in a CI environment
			if (process.env.CI) {
				process.kill(process.pid)
			}
		});
}

function concatenate_files() {
	// only concatenates files, not processed through rollup

	const files_to_concat = Object.keys(get_build_json('frappe'))
		.filter(filename => filename.startsWith('concat:'));

	files_to_concat.forEach(output_file => {
		const input_files = get_build_json('frappe')[output_file];
		let output_files = new Set();

		for (let file_name of input_files) {
			let prefix = get_app_path('frappe');
			if (file_name.startsWith('node_modules/')) {
				prefix = path.resolve(get_app_path('frappe'), '..');
			}
			const full_path = path.resolve(prefix, file_name);
			const output_file_path = output_file.slice('concat:'.length);
			const target_path = path.resolve(assets_path, output_file_path);

			if (!!output_files.has(output_file_path)) {
				log(`${chalk.green('✔')} Built ${output_file_path}`);
			} else {
				fs.writeFileSync(target_path, "", {flag:"w"});
			}

			fs.appendFile(target_path, `/* ${file_name} */\n` + fs.readFileSync(full_path), function (err) {
				if (err) throw err;
				output_files.add(output_file_path)
			});

		}
	});
}

function create_build_file() {
	const touch = require('touch');
	touch(path.join(sites_path, '.build'), { force: true });
}

function run_build_command_for_apps() {
	let cwd = process.cwd();
	apps_list.map(app => run_build_command_for_app(app))
	process.chdir(cwd);
}

function run_build_command_for_app(app) {
	if (app === 'frappe') return;
	let root_app_path = path.resolve(get_app_path(app), '..');
	let package_json = path.resolve(root_app_path, 'package.json');
	if (fs.existsSync(package_json)) {
		let package = require(package_json);
		if (package.scripts && package.scripts.build) {
			console.log('\nRunning build command for', chalk.bold(app));
			process.chdir(root_app_path);
			execSync(`yarn build ${memory_limit}`, { encoding: 'utf8', stdio: 'inherit' });
		}
	}
	if (global.gc) {global.gc();}
}

function ensure_js_css_dirs() {
	const paths = [
		path.resolve(assets_path, 'js'),
		path.resolve(assets_path, 'css')
	];
	paths.forEach(path => {
		if (!fs.existsSync(path)) {
			fs.mkdirSync(path);
		}
	});
}

function show_production_message() {
	const production = process.env.FRAPPE_ENV === 'production';
	log(chalk.yellow(`${production ? 'Production' : 'Development'} mode`));
}
