const merge = require('webpack-merge');
const AssetsPlugin = require('assets-webpack-plugin');
const path = require('path');
let common = require('./webpack.common.js');
const webpack = require('webpack');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
common.forEach((config, index) => {
    if (common[index].configName === 'base') {
        common[index].plugins = [
            new CleanWebpackPlugin(['assets/dist']),
            new ExtractTextPlugin('os-[name].[contenthash].dist.css'),
            new webpack.HashedModuleIdsPlugin(),
            new webpack.optimize.CommonsChunkPlugin({
                name: 'runner',
                minChunks: Infinity,
            }),
        ]
    }
    common[index] = merge(config,{
        devtool: 'source-map',
        plugins: [
            new webpack.DefinePlugin({
                'process.env': {
                    'NODE_ENV': JSON.stringify('production')
                }
            }),
            new webpack.optimize.UglifyJsPlugin({
                sourceMap: true,
                output: {
                    comments: false
                }
            }),
            new AssetsPlugin({
                filename: 'build-manifest.json',
                path: path.resolve(__dirname, 'assets/dist'),
                update: true
            })
        ]
    });
    //delete temporary named config item so no config errors
    delete common[index].configName;
});
module.exports = common;