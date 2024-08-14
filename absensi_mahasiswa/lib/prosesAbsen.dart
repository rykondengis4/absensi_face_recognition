import 'dart:convert';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:http/http.dart' as http;

const String apiUrl = "http://127.0.0.1:8000";

class AbsensiPage extends StatefulWidget {
  const AbsensiPage({super.key});

  @override
  State<AbsensiPage> createState() => _AbsensiPageState();
}

class _AbsensiPageState extends State<AbsensiPage> {
  bool _isLoading = false;
  Future<void>? _initData;

  @override
  void initState() {
    super.initState();
  }

  Future<void> _startAbsensi() async {
    setState(() {
      _isLoading = true;
    });

    final url = Uri.parse('$apiUrl/start');

    try {
      final response = await http.post(url);
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Absensi dimulai")),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Gagal memulai absensi")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error: $e")),
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
      body: FutureBuilder(
          future: _initData,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return Center(
                child: SpinKitSpinningLines(
                  color: Colors.white,
                  size: 50,
                ),
              );
            } else if (snapshot.hasError) {
              return Center(
                child: Text("Failed to load data"),
              );
            } else {
              return _buildMainContent();
            }
          }),
    );
  }

  Widget _buildMainContent() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(50),
        child: Container(
          height: 300,
          decoration: BoxDecoration(
              color: Colors.deepPurple[400],
              borderRadius: BorderRadius.circular(10)),
          child: Align(
            alignment: Alignment.center,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _isLoading
                      ? null
                      : () async {
                          await _startAbsensi();
                        },
                  child: _isLoading
                      ? SpinKitSpinningLines(
                          color: Colors.white,
                          size: 50,
                        )
                      : Text('Mulai Absensi'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
