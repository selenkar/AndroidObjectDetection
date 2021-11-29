package com.selenkarbuz.objectdetection;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.RequestBody;
import okhttp3.Response;
import pub.devrel.easypermissions.EasyPermissions;

public class MainActivity extends AppCompatActivity {

    final int SELECT_IMAGES = 1;
    ArrayList<Uri> selectedImagesPaths;
    boolean imagesSelected = false;
    ImageView imageView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        imageView = findViewById(R.id.imageView);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        EasyPermissions.onRequestPermissionsResult(requestCode, permissions, grantResults, this);
    }

    public void connectServer(View v) {

        TextView responseText = findViewById(R.id.responseText);
        if (imagesSelected == false) {
            responseText.setText("No image selected to upload. \nSelect image and try again.");
            return;
        }

        responseText.setText("Sending the files. Please wait...");

        // API url
        String postUrl = "http://" + "192.168.1.69" + ":" + 5000 + "/predict/";

        MultipartBody.Builder multipartBodyBuilder = new MultipartBody.Builder().setType(MultipartBody.FORM);

        for (int i = 0; i < selectedImagesPaths.size(); i++) {
            byte[] byteArray = null;
            try {
                InputStream inputStream = getContentResolver().openInputStream(selectedImagesPaths.get(i));
                ByteArrayOutputStream byteBuffer = new ByteArrayOutputStream();
                int bufferSize = 1024;
                byte[] buffer = new byte[bufferSize];

                int len = 0;
                while ((len = inputStream.read(buffer)) != -1) {
                    byteBuffer.write(buffer, 0, len);
                }
                byteArray = byteBuffer.toByteArray();

            } catch(Exception e) {
                Toast.makeText(MainActivity.this, "Please make sure the selected file is an image.", Toast.LENGTH_LONG).show();
            }
            multipartBodyBuilder.addFormDataPart("image" + i, "input_img.jpg", RequestBody.create(MediaType.parse("image/*jpg"), byteArray));
        }
        RequestBody postBodyImage = multipartBodyBuilder.build();

        postRequest(postUrl, postBodyImage);
    }

    void postRequest(String postUrl, RequestBody postBody) {

        OkHttpClient client = new OkHttpClient();

        Request request = new Request.Builder()
                .url(postUrl)
                .post(postBody)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                call.cancel();
                Log.d("FAIL", e.getMessage());
                runOnUiThread(() -> {
                    TextView responseText = findViewById(R.id.responseText);
                    responseText.setText("Failed to connect to server. Please try again.");
                });
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                runOnUiThread(() -> {
                    TextView responseText = findViewById(R.id.responseText);
                    try {
                        responseText.setText(response.body().string());
                    } catch (IOException e) {
                        responseText.setText("Please try again.");
                        e.printStackTrace();
                    }
                });
            }
        });
    }

    public void selectImage(View v) {
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(Intent.createChooser(intent, "Select Picture"), SELECT_IMAGES);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        try {
            if (requestCode == SELECT_IMAGES && resultCode == RESULT_OK && data != null) {
                selectedImagesPaths = new ArrayList<>();
                if (data.getData() != null) {
                    Uri uri = data.getData();
                    Log.d("ImageDetails", "URI : " + uri);
                    selectedImagesPaths.add(uri);
                    imagesSelected = true;
                    imageView.setImageURI(selectedImagesPaths.get(0));
                }
            }
            else {
                Toast.makeText(this, "You haven't picked any image.", Toast.LENGTH_LONG).show();
            }
        } catch (Exception e) {
            Toast.makeText(this, "Something went wrong.", Toast.LENGTH_LONG).show();
            e.printStackTrace();
        }
    }

}