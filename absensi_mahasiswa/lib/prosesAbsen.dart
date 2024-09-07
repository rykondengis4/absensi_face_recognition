import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:geolocator/geolocator.dart';
import 'package:quickalert/quickalert.dart';
import 'dart:math';
import 'package:http/http.dart' as http;

const String apiUrl = "http://127.0.0.1:8000";

class AbsensiPage extends StatefulWidget {
  const AbsensiPage({super.key});

  @override
  State<AbsensiPage> createState() => _AbsensiPageState();
}

class _AbsensiPageState extends State<AbsensiPage> {
  bool _isLoading = false;

  Future<void> _startCamera() async {
    final url = Uri.parse('$apiUrl/start');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        print("Kamera dimulai");
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Gagal memulai kamera")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Terjadi kesalahan: $e")),
      );
    }
  }

  Future<void> _stopCamera() async {
    final url = Uri.parse('$apiUrl/stop');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        print("Kamera dihentikan");
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Gagal memulai kamera")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Terjadi kesalahan: $e")),
      );
    }
  }

  bool isWithinCampus(double userLat, double userLon, double campusLat,
      double campusLon, double radiusKm) {
    const double earthRadiusKm = 6371.0;
    double dLat = _degreesToRadians(campusLat - userLat);
    double dLon = _degreesToRadians(campusLon - userLon);

    double lat1 = _degreesToRadians(userLat);
    double lat2 = _degreesToRadians(campusLat);

    double a = sin(dLat / 2) * sin(dLat / 2) +
        sin(dLon / 2) * sin(dLon / 2) * cos(lat1) * cos(lat2);
    double c = 2 * atan2(sqrt(a), sqrt(1 - a));
    double distance = earthRadiusKm * c;

    return distance <= radiusKm;
  }

  double _degreesToRadians(double degrees) {
    return degrees * pi / 180;
  }

  Future<void> _startAbsensi() async {
    setState(() {
      _isLoading = true;
    });

    try {
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      // double campusLat = 0.52301;
      // double campusLon = 123.11148450803552;
      // double radiusKm = 1;

      double campusLat = 0.57755678;
      double campusLon = 123.06322300000001;
      double radiusKm = 1;

      if (isWithinCampus(position.latitude, position.longitude, campusLat,
          campusLon, radiusKm)) {
        _startCamera();
        QuickAlert.show(
          context: context,
          type: QuickAlertType.loading,
          title: 'Loading',
          text: 'Tunggu Hingga Proses Absensi selesai',
        );
      } else {
        QuickAlert.show(
          context: context,
          type: QuickAlertType.warning,
          title: 'Peringatan',
          text: 'Opps... Sepertinya anda tidak berada di lokasi kampus',
        );
        _stopCamera();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Terjadi kesalahan: $e")),
      );
      QuickAlert.show(
        context: context,
        type: QuickAlertType.error,
        title: 'Oops...',
        text: 'Terjadi kesalahan: $e',
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.deepPurple[200],
      appBar: AppBar(
        backgroundColor: Colors.deepPurple,
        title: Center(
          child: Text(
            "Halaman Absensi",
            style: TextStyle(
              color: Colors.white,
            ),
          ),
        ),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Container(
            height: 300,
            decoration: BoxDecoration(
              color: Colors.deepPurple[400],
              borderRadius: BorderRadius.circular(10),
            ),
            child: _isLoading
                ? Center(
                    child: SpinKitSpinningLines(
                      color: Colors.white,
                      size: 50,
                    ),
                  )
                : _buildMainContent(),
          ),
        ),
      ),
    );
  }

  Widget _buildMainContent() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          ElevatedButton(
            onPressed: _isLoading ? null : _startAbsensi,
            child: Text('Mulai Absensi'),
          ),
        ],
      ),
    );
  }
}
