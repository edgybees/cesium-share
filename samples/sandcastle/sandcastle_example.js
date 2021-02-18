var viewer = new Cesium.Viewer("cesiumContainer");
var options = {
  camera: viewer.scene.camera,
  canvas: viewer.scene.canvas,
};
Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2NzQ3MjZmYy04YjViLTRhNzQtOWE5YS1jMDBhNzMxZjU3NmQiLCJpZCI6MjEyMDMsInNjb3BlcyI6WyJhc3IiLCJnYyJdLCJpYXQiOjE1NzkxMDU3MTN9.BpzcztkZcE4h7pUPpjPdkwQ7DdwSFGGwP12XnhLtQig";


Sandcastle.addToolbarMenu(
  [
    {
      text: "KML - Global Science Facilities",
      onselect: function () {
        viewer.camera.flyHome(0);

        var promise = Cesium.IonResource.fromAssetId(298383).then(function (resource) {
          return Cesium.KmlDataSource.load(resource, {
            camera: viewer.scene.camera,
            canvas: viewer.scene.canvas,
          });
        })
          .then(function (dataSource) {
            return viewer.dataSources.add(dataSource);
          })
          .otherwise(function (error) {
            console.log(error);
          });

        viewer.camera.position = Cesium.Cartographic.toCartesian(new Cesium.Cartographic(0, 0, 500));
        viewer.camera.setView({
          orientation: Cesium.HeadingPitchRoll.fromDegrees(0, -90, 0)
        });
        // viewer.camera.frustum = new Cesium.PerspectiveFrustum({
        //  fov: 60 * (Cesium.Math.PI / 180),
        //  aspectRatio: 16/9,
        // });

      },
    },
  ],
  "toolbar"
);

Sandcastle.reset = function () {
  viewer.dataSources.removeAll();
  viewer.clock.clockRange = Cesium.ClockRange.UNBOUNDED;
  viewer.clock.clockStep = Cesium.ClockStep.SYSTEM_CLOCK;
};
