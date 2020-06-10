const constraints = {
    video: {width: {exact: 640}, height: {exact: 480}},
    audio: false
};

const img = document.querySelector('#photoPreview');
const video = document.querySelector('#videoPreview');

let status = 'initial';

function hasGetUserMedia() {
  return !!(navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia);
}

function startVideoPreview() {
  navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
    handleSuccess(stream);
  }).catch(handleError);
}

function stopVideoPreview() {
    let stream = video.srcObject;
    if (stream !== null) {
        let tracks = stream.getTracks();

        for (let i = 0; i < tracks.length; i++) {
            let track = tracks[i];
            track.stop();
        }

        video.srcObject = null;
    }
}

function takePhoto() {
  let canvas = document.createElement('canvas');

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  let imgString = canvas.toDataURL('image/webp');
  img.src = imgString;

  $('#id_data').val(imgString);
}

function handleSuccess(stream) {
  let video = document.querySelector('#videoPreview');
  video.srcObject = stream;
}

function handleError(error) {
  $('#photoPreview').hide();
  $('#videoPreview').hide();
  $('#cameraError').show();
  $('#btnTakePhoto').attr('disabled', true);
}

function enableCropper() {
    let $image = $('#photoPreview');

    $image.cropper({
        aspectRatio: 2 / 3,
        crop: function(event) {
            $('#id_x').val(event.detail.x);
            $('#id_y').val(event.detail.y);
            $('#id_width').val(event.detail.width);
            $('#id_height').val(event.detail.height);
        }
    });

}

function disableCropper() {
    let $image = $('#photoPreview');
    $image.cropper('destroy');
}

function initModal() {
    // default status
    status = 'initial';

    // make sure the video is stopped
    stopVideoPreview();

    // hide everything on start
    $('#videoPreview').hide();
    $('#photoPreview').hide();
    $('#cameraError').hide();

    // default button
    $('#btnTakePhoto')
        .html('<i class="fa fa-play"></i>Habilitar cámara')
        .attr('class', 'btn btn-outline-primary mt-2');
}

window.onload = function() {
  $('#btnTakePhoto').on('click',function() {
      if (status === 'initial') {
          disableCropper();
          startVideoPreview();

          $('#videoPreview').show();
          $('#photoPreview').hide();
          $('#btnTakePhoto')
              .html('<i class="fa fa-camera"></i>Tomar foto')
              .attr('class', 'btn btn-outline-primary mt-2');
          $('#btnPhotoSubmit').attr('disabled', true);

          status = 'videoPreview';
      } else if (status === 'videoPreview') {
          takePhoto();
          stopVideoPreview();
          enableCropper();

          $('#videoPreview').hide();
          $('#photoPreview').show();
          $('#btnTakePhoto')
              .html('<i class="fa fa-undo"></i>Volver a tomar')
              .attr('class', 'btn btn-outline-secondary mt-2');
          $('#btnPhotoSubmit').attr('disabled', false);

          status = 'initial';
      }
  });

    $('#takePhotoModal').on('shown', function () {
        console.log('modal shown');
    }).on('hidden', function () {
        console.log('modal hidden');
    });

    initModal();
};
