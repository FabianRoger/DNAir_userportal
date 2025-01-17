import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { 
  MapPin, 
  Calendar, 
  AlertTriangle, 
  Search, 
  Database, 
  LineChart as LineChartIcon, 
  Users 
} from 'lucide-react';


const ProjectDashboard = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [map, setMap] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const API_URL = process.env.REACT_APP_API_URL;
        const response = await fetch(`${API_URL}/users/`);
        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError('Failed to fetch users');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  useEffect(() => {
    if (!selectedUser) return;
    
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const API_URL = process.env.REACT_APP_API_URL;
        const response = await fetch(`${API_URL}/projects/${selectedUser}`);
        const data = await response.json();
        setProjects(data);
      } catch (err) {
        setError('Failed to fetch projects');
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [selectedUser]);

  useEffect(() => {
    if (!selectedProject) return;

    const fetchProjectData = async () => {
      try {
        setLoading(true);
        const API_URL = process.env.REACT_APP_API_URL;
        const response = await fetch(`${API_URL}/projects/${selectedProject}/data`);
        const data = await response.json();
        setProjectData(data);
      } catch (err) {
        setError('Failed to fetch project data');
      } finally {
        setLoading(false);
      }
    };

    fetchProjectData();
  }, [selectedProject]);

  // Initialize map when project data changes
  useEffect(() => {
    if (projectData?.locationData?.length > 0) {
      // Clean up existing map
      if (map) {
        map.remove();
      }

      const L = window.L;
      const newMap = L.map('map').setView([
        projectData.locationData[0].latitude,
        projectData.locationData[0].longitude
      ], 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(newMap);

      // Add markers for each sampling location
      projectData.locationData.forEach(location => {
        L.marker([location.latitude, location.longitude])
          .bindPopup(`${location.name}<br>Samples: ${location.samples}`)
          .addTo(newMap);
      });

      setMap(newMap);
    }

    return () => {
      if (map) {
        map.remove();
      }
    };
  }, [projectData]);

  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-6">
      {/* User and Project Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Select User
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Select value={selectedUser} onValueChange={setSelectedUser}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a user" />
              </SelectTrigger>
              <SelectContent>
                {users.map(user => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Select Project</CardTitle>
          </CardHeader>
          <CardContent>
            <Select 
              value={selectedProject} 
              onValueChange={setSelectedProject}
              disabled={!selectedUser || projects.length === 0}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder={
                  !selectedUser 
                    ? "Select a user first" 
                    : projects.length === 0 
                      ? "No projects available" 
                      : "Select a project"
                } />
              </SelectTrigger>
              <SelectContent>
                {projects.map(project => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      </div>

      {loading && (
        <div className="flex justify-center p-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}

      {projectData && (
        <>
          {/* Metrics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Species</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {projectData.metrics.speciesRichness}
                </div>
                <p className="text-sm text-gray-500">Total species detected</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Sampling Sites</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {projectData.locationData?.length || 0}
                </div>
                <p className="text-sm text-gray-500">Active sampling sites</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg text-orange-600">Invasive Species</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">
                  {projectData.metrics.invasiveSpecies}
                </div>
                <p className="text-sm text-gray-500">Species of concern</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg text-green-600">Protected Species</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {projectData.metrics.protectedSpecies}
                </div>
                <p className="text-sm text-gray-500">Conservation status</p>
              </CardContent>
            </Card>
          </div>

          {/* Tabbed Interface */}
          <Tabs defaultValue="overview" className="w-full">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="data">Data</TabsTrigger>
              <TabsTrigger value="analysis">Analysis</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Map */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="h-5 w-5" />
                      Sampling Locations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div id="map" className="h-96 w-full rounded-lg" />
                  </CardContent>
                </Card>

                {/* Recent Findings */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5" />
                      Recent Findings
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {projectData.recentFindings?.map((finding, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <div>
                            <span className={`text-sm ${
                              finding.type === 'invasive' 
                                ? 'text-orange-500' 
                                : 'text-green-500'
                            }`}>
                              {finding.type.toUpperCase()}
                            </span>
                            <p className="font-medium">{finding.species}</p>
                          </div>
                          <div className="text-sm text-gray-500">
                            {finding.date}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Sampling Details */}
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle>Sampling Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {projectData.locationData?.map((location, index) => (
                      <div key={index} className="p-4 bg-gray-50 rounded-lg">
                        <h3 className="font-semibold">{location.name}</h3>
                        <p className="text-sm text-gray-600">Samples: {location.samples}</p>
                        <p className="text-sm text-gray-600">
                          Location: {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="data">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Data Explorer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Search className="h-4 w-4 text-gray-500" />
                      <input
                        type="text"
                        placeholder="Search species or locations..."
                        className="w-full p-2 border rounded"
                      />
                    </div>
                    {projectData.otuData && (
                      <div className="overflow-x-auto">
                        <table className="w-full border-collapse text-sm">
                          <thead>
                            <tr className="bg-gray-50">
                              <th className="border p-2 text-left">Species</th>
                              <th className="border p-2 text-left">Status</th>
                              <th className="border p-2 text-left">Abundance</th>
                              <th className="border p-2 text-left">Location</th>
                            </tr>
                          </thead>
                          <tbody>
                            {projectData.otuData.map((row, index) => (
                              <tr key={index} className="hover:bg-gray-50">
                                <td className="border p-2">{row.species}</td>
                                <td className="border p-2">
                                  <span className={
                                    row.status === 'invasive' 
                                      ? 'text-orange-500' 
                                      : row.status === 'protected' 
                                        ? 'text-green-500' 
                                        : 'text-gray-500'
                                  }>
                                    {row.status}
                                  </span>
                                </td>
                                <td className="border p-2">{row.abundance}</td>
                                <td className="border p-2">{row.location}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analysis">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <LineChartIcon className="h-5 w-5" />
                    Biodiversity Trends
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={projectData.timeSeriesData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="speciesCount"
                          stroke="#8884d8" 
                          name="Species Count" 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="diversity" 
                          stroke="#82ca9d" 
                          name="Diversity Index" 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
};

export default ProjectDashboard;