import 'dart:convert';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:dropdown_search/dropdown_search.dart';
import 'package:http/http.dart' as http;

class AbsensiPage extends StatefulWidget {
  const AbsensiPage({super.key});

  @override
  State<AbsensiPage> createState() => _AbsensiPageState();
}

class _AbsensiPageState extends State<AbsensiPage> {
  final String apiUrl = "http://127.0.0.1:8000";
  bool _isLoading = false;
  List<String> mataKuliahList = [];
  List<String> dosenList = [];
  String? selectedMataKuliah;
  String? selectedDosen;
  Future<void>? _initData;

  @override
  void initState() {
    super.initState();
    _initData = _fetchInitData();
  }

  Future<void> _fetchInitData() async {
    await Future.wait([_fetchMataKuliah(), _fetchDosen()]);
  }

  Future<void> _fetchMataKuliah() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.get(Uri.parse('$apiUrl/mata_kuliah'));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          mataKuliahList = List<String>.from(data['mata_kuliah']);
          _isLoading = false;
        });
      } else {
        print("Failed to fetch mata kuliah");
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error: $e")),
      );
    }
  }

  Future<void> _fetchDosen() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.get(Uri.parse('$apiUrl/dosen'));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          dosenList = List<String>.from(data['dosen']);
          _isLoading = false;
        });
      } else {
        print("Failed to fetch dosen");
      }
    } catch (e) {
      print("Error: $e");
    }
  }

  Future<void> _startAbsensi() async {
    if (selectedMataKuliah == null || selectedDosen == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Pilih mata kuliah dan dosen terlebih dahulu")),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final url = Uri.parse('$apiUrl/start');

    try {
      final response = await http.post(url);

      if (response.statusCode == 200) {
        print("Memulai Absensi");
      } else {
        print("Gagal memulai absensi");
      }
    } catch (e) {
      print("Error : Maintenence $e");
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
          height: 500,
          decoration: BoxDecoration(
              color: Colors.deepPurple[400],
              borderRadius: BorderRadius.circular(10)),
          child: Align(
            alignment: Alignment.center,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        height: 300,
                        width: 400,
                        margin: EdgeInsets.all(20),
                        decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(20)),
                        child: DropdownSearch<String>(
                          popupProps: PopupProps.dialog(
                            showSelectedItems: true,
                            // disabledItemFn: (String s) => s.startsWith('I'),
                          ),
                          items: mataKuliahList,
                          dropdownDecoratorProps: DropDownDecoratorProps(
                            dropdownSearchDecoration: InputDecoration(
                              labelText: "Mata Kuliah",
                              hintText: "menu mata kuliah",
                            ),
                          ),
                          onChanged: (value) {
                            setState(() {
                              selectedMataKuliah = value;
                            });
                          },
                          selectedItem: mataKuliahList.first,
                        ),
                      ),
                      Container(
                        height: 300,
                        width: 400,
                        decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(20)),
                        child: DropdownSearch<String>(
                          popupProps: PopupProps.dialog(
                            showSelectedItems: true,
                          ),
                          items: dosenList,
                          dropdownDecoratorProps: DropDownDecoratorProps(
                            dropdownSearchDecoration: InputDecoration(
                              labelText: "Dosen Pengampu",
                              hintText: "menu dosen",
                            ),
                          ),
                          onChanged: (value) {
                            setState(() {
                              selectedDosen = value;
                            });
                          },
                          selectedItem: dosenList.first,
                        ),
                      ),
                    ],
                  ),
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: (_isLoading ||
                          selectedMataKuliah == null ||
                          selectedDosen == null)
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
