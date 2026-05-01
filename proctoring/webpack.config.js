const path = require('path');
const webpack = require('webpack');

module.exports = {
    entry: './index.tsx',
    mode: 'development',
    output: {
        filename: 'proctoring.bundle.js',
        path: path.resolve(__dirname, '../hiring/static/hiring/js/proctoring'),
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('development'),
            'process.env': JSON.stringify({})
        })
    ],
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
    },
};
