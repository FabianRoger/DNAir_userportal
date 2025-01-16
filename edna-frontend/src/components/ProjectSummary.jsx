import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { AlertTriangle, Users, MapPin, FileText } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL;

const ProjectSummary = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        console.log('Fetching users from:', `${API_URL}/users/`);
        const response = await axios.get(`${API_URL}/users/`);
        console.log('Users response:', response.data);
        setUsers(response.data);
      } catch (err) {
        console.error('Error fetching users:', err);
        setError('Failed to fetch users');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  useEffect(() => {
    const fetchProjects = async () => {
      if (!selectedUser) return;
      
      try {
        setLoading(true);
        console.log('Fetching projects for user:', selectedUser);
        const response = await axios.get(`${API_URL}/projects/${selectedUser}`);
        console.log('Projects response:', response.data);
        setProjects(response.data);
      } catch (err) {
        console.error('Error fetching projects:', err);
        setError('Failed to fetch projects');
      } finally {
        setLoading(false);
      }
    };

    if (selectedUser) {
      fetchProjects();
    }
  }, [selectedUser]);

  useEffect(() => {
    const fetchProjectData = async () => {
      if (!selectedProject) return;
      
      try {
        setLoading(true);
        console.log('Fetching project data:', selectedProject);
        const response = await axios.get(`${API_URL}/projects/${selectedProject}/data`);
        console.log('Project data response:', response.data);
        setProjectData(response.data);
      } catch (err) {
        console.error('Error fetching project data:', err);
        setError('Failed to fetch project data');
      } finally {
        setLoading(false);
      }
    };

    if (selectedProject) {
      fetchProjectData();
    }
  }, [selectedProject]);

  useEffect(() => {
    if (projectData?.locationData?.length > 0) {
      // Initialize map
      const L = window.L;
      const map = L.map('map').setView([
        projectData.locationData[0].latitude,
        projectData.locationData[0].longitude
      ], 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);

      // Add markers for each sampling location
      projectData.locationData.forEach(location => {
        L.marker([location.latitude, location.longitude])
          .bindPopup(`${location.name}<br>Samples: ${location.samples}`)
          .addTo(map);
      });

      // Cleanup
      return () => map.remove();
    }
  }, [projectData]);

  const handleUserChange = (userId) => {
    setSelectedUser(userId);
    setSelectedProject('');
    setProjectData(null);
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* User Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Select User
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Select value={selectedUser} onValueChange={handleUserChange}>
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

        {/* Project Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Select Project
            </CardTitle>
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
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}

      {projectData && (
        <>
          {/* Metrics Summary */}
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
                  {projectData.locationData.length}
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

          {/* Map */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Sampling Locations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div id="map" className="h-96 w-full rounded-lg"></div>
            </CardContent>
          </Card>

          {/* Sampling Details */}
          <Card>
            <CardHeader>
              <CardTitle>Sampling Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {projectData.locationData.map((location, index) => (
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
        </>
      )}
    </div>
  );
};

export default ProjectSummary;