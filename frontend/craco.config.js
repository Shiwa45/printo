module.exports = {
	webpack: {
		configure: (webpackConfig) => {
			// 1) Ensure any existing source-map-loader usage excludes the problematic paths
			const rules = (webpackConfig.module && webpackConfig.module.rules) ? webpackConfig.module.rules : [];
			for (const rule of rules) {
				if (rule.oneOf) {
					for (const one of rule.oneOf) {
						if (one.use) {
							const useArr = Array.isArray(one.use) ? one.use : [one.use];
							for (const u of useArr) {
								if (u.loader && u.loader.includes('source-map-loader')) {
									u.exclude = [
										/node_modules\/react-design-editor\/node_modules\/.*/,
										/node_modules\/react-design-editor\/node_modules\/react\/.*/,
										/node_modules\/react-design-editor\/node_modules\/react-dom\/.*/,
									];
								}
							}
						}
					}
				}
			}

			// 2) Add a defensive top-level rule to exclude source-map-loader from those paths if it appears elsewhere
			webpackConfig.module.rules.push({
				test: /\.js$/,
				enforce: 'pre',
				exclude: [
					/node_modules\/react-design-editor\/node_modules\/.*/,
					/node_modules\/react-design-editor\/node_modules\/react\/.*/,
					/node_modules\/react-design-editor\/node_modules\/react-dom\/.*/,
				],
				use: [
					{
						loader: require.resolve('source-map-loader'),
						options: {},
					},
				],
			});

			return webpackConfig;
		},
	},
};
