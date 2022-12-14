const { defineConfig } = require("cypress");
require('dotenv').config()

module.exports = defineConfig({
  defaultCommandTimeout: 30000,
  requestTimeout: 30000,
  viewportHeight: 800,
  viewportWidth: 800,
  videoCompression: false,
  e2e: {
    baseUrl: 'http://127.0.0.1:5000/',
    projectId: "scpmmm",
    setupNodeEvents(on, config) {
      // implement node event listeners here
      config.env = {
        ...process.env,
        ...config.env
      }
      return config 
    },
    screenshotOnRunFailure:true,
    trashAssetsBeforeRuns:false,
    experimentalSessionAndOrigin:true,
  }
});
