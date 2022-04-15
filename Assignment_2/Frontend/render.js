document.getElementById('displaytext').style.display = 'none';
 
console.log("test comment !!!");

function searchPhoto() {
 var apigClient = apigClientFactory.newClient(
   {apiKey: "************************"}
 );
 
 var user_message = document.getElementById('note-textarea').value;
  console.log("User message input: ", user_message);
 
 var body = {};
 var params = { q: user_message };
 var additionalParams = {
   headers: {
     'Content-Type': 'application/json',
   },
 };
 console.log("params => ", params);
 
 apigClient
   .searchGet(params, body, additionalParams)
   .then(function (res) {
     var data = {};
     var data_array = [];
     console.log('Before getting the response');
    
    
     resp_data = res.data;
     length_of_response = resp_data.length;
    
     console.log('After getting the response');
 
     // console.log(resp_data);
    
     console.log("IGNORE ME");
     console.log(resp_data['body']['results']);
      
     if (resp_data['body']['results'].length == 0) {
       document.getElementById('displaytext').innerHTML =
         'Sorry could not find the image. Try again!' ;
       document.getElementById('displaytext').style.display = 'block';
     }
 
     resp_data = resp_data['body']['results']
    
     resp_data.forEach(function (obj) {
       var img = new Image();
       console.log(obj);
       img.src = obj;
       img.setAttribute('class', 'banner-img');
       img.setAttribute('alt', 'effy');
       document.getElementById('displaytext').innerHTML =
         'Images returned are : ';
       document.getElementById('img-container').appendChild(img);
       document.getElementById('displaytext').style.display = 'block';
     });
   })
   .catch(function (result) {});
}
 
function getBase64(file) {
 return new Promise((resolve, reject) => {
   const reader = new FileReader();
   reader.readAsDataURL(file);
   // reader.onload = () => resolve(reader.result)
   reader.onload = () => {
     let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
    //  let encoded = Buffer.from(req.body.imageBinary.replace(/^data:image\/\w+;base64,/, ""),'base64');
     if (encoded.length % 4 > 0) {
       encoded += '='.repeat(4 - (encoded.length % 4));
     }
     resolve(encoded);
   };
   reader.onerror = (error) => reject(error);
 });
}


function uploadPhoto(){
var tag_image = note_customtag.value.split(",");
var file = document.getElementById('file_path').files[0];
var type_file_up = file.type;
var name_f = file.name;
console.log("File Type ===>", type_file_up)
console.log("Code Pipeline Check Here !!!!")
var reader = new FileReader();
reader.readAsArrayBuffer(file);
reader.onload = function (event) {
    console.log("Reader Object",event.target.result)
    console.log("Reader ",reader.result)
    // var myHeaders = new Headers();
    // myHeaders.append("x-amz-meta-customLabels",  note_customtag.value);
    // myHeaders.append("Content-Type", type_file_up);
    // console.log("Header here --->>>", myHeaders)
    var file = new Uint8Array(reader.result);
    var requestOptions = {
    method: 'PUT',
    headers: {"x-amz-meta-customLabels" : tag_image, "Content-Type": type_file_up},
    body: file,
    redirect: 'follow'
    };

    console.log("re headers ====>>>>", requestOptions);
    fetch(`https://16577esc56.execute-api.us-east-1.amazonaws.com/alpha/upload/album-photo-store/${name_f}`, requestOptions)
    .then(response => response.text())
    .then(result => console.log(result)).then(alert("Photo uploaded successfully!"))
    .catch(error => console.log('error', error));
}
}