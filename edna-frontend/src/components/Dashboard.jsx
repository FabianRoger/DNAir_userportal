import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Card,
  CardContent,
  CardDescription,
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

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard = () => {
  // State management
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [projectData, setProjectData] = useState({
    metrics: {
      speciesRichness: 0,
      phylogeneticDiversity: 0,
      invasiveSpecies: 0,
      protectedSpecies: 0
    },
    recentFindings: [],
    timeSeriesData: [],
    locationData: [],
    otuData: []
  });

  // Fetch users on component mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/users/`);
        setUsers(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch users');
        console.error('Error fetching users:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  // Fetch projects when user is selected
  useEffect(() => {
    const fetchProjects = async () => {
      if (!selectedUser) return;
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/projects/${selectedUser}`);
        setProjects(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch projects');
        console.error('Error fetching projects:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, [selectedUser]);

  // Fetch project data when project is selected
  useEffect(() => {
    const fetchProjectData = async () => {
      if (!selectedProject) return;
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/projects/${selectedProject}/data`);
        setProjectData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch project data');
        console.error('Error fetching project data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProjectData();
  }, [selectedProject]);

  // Biodiversity metrics chart component
  const BiodiversityChart = () => (
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
            dataKey="speciesRichness" 
            stroke="#8884d8" 
            name="Species Richness" 
          />
          <Line 
            type="monotone" 
            dataKey="phylogeneticDiversity" 
            stroke="#82ca9d" 
            name="Phylogenetic Diversity" 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  // Data table component for OTU data
  const DataTable = () => (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-slate-100">
            <th className="border p-2 text-left">OTU ID</th>
            <th className="border p-2 text-left">Species</th>
            <th className="border p-2 text-left">Abundance</th>
            <th className="border p-2 text-left">Status</th>
          </tr>
        </thead>
        <tbody>
          {projectData.otuData.map((row, index) => (
            <tr key={index} className="hover:bg-slate-50">
              <td className="border p-2">{row.otuId}</td>
              <td className="border p-2">{row.species}</td>
              <td className="border p-2">{row.abundance}</td>
              <td className="border p-2">
                <span className={
                  row.status === 'invasive' 
                    ? 'text-amber-500' 
                    : row.status === 'protected' 
                      ? 'text-green-500' 
                      : 'text-slate-500'
                }>
                  {row.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-4">
      {/* User and Project Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Project Selection
          </CardTitle>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Select value={selectedUser} onValueChange={setSelectedUser}>
            <SelectTrigger className="w-64">
              <SelectValue placeholder="Select User" />
            </SelectTrigger>
            <SelectContent>
              {users.map(user => (
                <SelectItem key={user.id} value={user.id}>
                  {user.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select 
            value={selectedProject} 
            onValueChange={setSelectedProject}
            disabled={!selectedUser}
          >
            <SelectTrigger className="w-64">
              <SelectValue placeholder="Select Project" />
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

      {error && (
        <Card className="bg-red-50">
          <CardContent className="p-4 text-red-500">
            {error}
          </CardContent>
        </Card>
      )}

      {loading ? (
        <Card>
          <CardContent className="p-4 text-center">
            Loading...
          </CardContent>
        </Card>
      ) : selectedProject ? (
        <>
          {/* Metrics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="p-4">
                <CardTitle className="text-2xl">
                  {projectData.metrics.speciesRichness}
                </CardTitle>
                <CardDescription>Species Detected</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="p-4">
                <CardTitle className="text-2xl">
                  {projectData.metrics.phylogeneticDiversity}
                </CardTitle>
                <CardDescription>Phylogenetic Diversity</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="p-4">
                <CardTitle className="text-2xl text-amber-500">
                  {projectData.metrics.invasiveSpecies}
                </CardTitle>
                <CardDescription>Invasive Species</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="p-4">
                <CardTitle className="text-2xl text-green-500">
                  {projectData.metrics.protectedSpecies}
                </CardTitle>
                <CardDescription>Protected Species</CardDescription>
              </CardHeader>
            </Card>
          </div>

          {/* Main Content */}
          <Tabs defaultValue="overview" className="w-full">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="data">Raw Data</TabsTrigger>
              <TabsTrigger value="analysis">Analysis</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="h-5 w-5" />
                      Sampling Locations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 bg-slate-100 rounded flex items-center justify-center">
                      Map Visualization
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5" />
                      Recent Findings
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {projectData.recentFindings.map((finding, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                          <div>
                            <span className={`text-sm ${
                              finding.type === 'invasive' 
                                ? 'text-amber-500' 
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
            </TabsContent>

            <TabsContent value="data">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Raw Data Explorer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Search className="h-4 w-4 text-gray-500" />
                      <input
                        type="text"
                        placeholder="Search sequences, species, or locations..."
                        className="w-full p-2 border rounded"
                      />
                    </div>
                    <DataTable />
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
                  <BiodiversityChart />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      ) : null}
    </div>
  );
};

export default Dashboard;