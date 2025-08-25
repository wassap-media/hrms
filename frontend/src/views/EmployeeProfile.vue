<template>
	<BaseLayout>
		<template #body>
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
				<!-- Employee Header -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-4">
							<div class="w-16 h-16 bg-gradient-to-br from-pink-400 to-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
								{{ employeeInitials }}
							</div>
							<div>
								<h1 class="text-3xl font-bold text-gray-900">{{ employee.name }}</h1>
								<div class="flex items-center space-x-3 mt-2">
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
										{{ employee.status || 'Active' }}
									</span>
									<span class="text-sm text-gray-500">{{ employee.employee_id }}</span>
								</div>
							</div>
						</div>
						<div class="flex items-center space-x-3">
							<button class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
								Print
							</button>
							<button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
								Save
							</button>
						</div>
					</div>
				</div>

				<!-- Tab Navigation -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
					<div class="border-b border-gray-200">
						<nav class="flex space-x-8 px-6" aria-label="Tabs">
							<button
								v-for="tab in tabs"
								:key="tab.id"
								@click="activeTab = tab.id"
								:class="[
									activeTab === tab.id
										? 'border-blue-500 text-blue-600'
										: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
									'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
								]"
							>
								{{ tab.label }}
							</button>
						</nav>
					</div>

					<!-- Tab Content -->
					<div class="p-6">
						<!-- Overview Tab -->
						<div v-if="activeTab === 'overview'" class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
								<div class="bg-gray-50 p-4 rounded-lg">
									<h3 class="text-lg font-medium text-gray-900 mb-2">Basic Information</h3>
									<div class="space-y-2 text-sm">
										<div><span class="font-medium">Name:</span> {{ employee.name }}</div>
										<div><span class="font-medium">Employee ID:</span> {{ employee.employee_id }}</div>
										<div><span class="font-medium">Status:</span> {{ employee.status }}</div>
									</div>
								</div>
								<div class="bg-gray-50 p-4 rounded-lg">
									<h3 class="text-lg font-medium text-gray-900 mb-2">Company Details</h3>
									<div class="space-y-2 text-sm">
										<div><span class="font-medium">Department:</span> {{ employee.department }}</div>
										<div><span class="font-medium">Designation:</span> {{ employee.designation }}</div>
										<div><span class="font-medium">Branch:</span> {{ employee.branch }}</div>
									</div>
								</div>
								<div class="bg-gray-50 p-4 rounded-lg">
									<h3 class="text-lg font-medium text-gray-900 mb-2">Quick Actions</h3>
									<div class="space-y-2">
										<button class="w-full text-left text-sm text-blue-600 hover:text-blue-800">
											Edit Profile
										</button>
										<button class="w-full text-left text-sm text-blue-600 hover:text-blue-800">
											View Documents
										</button>
										<button class="w-full text-left text-sm text-blue-600 hover:text-blue-800">
											Request Changes
										</button>
									</div>
								</div>
							</div>
						</div>

						<!-- Personal Details Tab -->
						<div v-if="activeTab === 'personal-details'" class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Personal Information</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Full Name</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Date of Birth</label>
											<input type="date" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Gender</label>
											<select class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
												<option>Male</option>
												<option>Female</option>
												<option>Other</option>
											</select>
										</div>
									</div>
								</div>
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Additional Details</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Blood Group</label>
											<select class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
												<option>A+</option>
												<option>A-</option>
												<option>B+</option>
												<option>B-</option>
												<option>AB+</option>
												<option>AB-</option>
												<option>O+</option>
												<option>O-</option>
											</select>
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Marital Status</label>
											<select class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
												<option>Single</option>
												<option>Married</option>
												<option>Divorced</option>
												<option>Widowed</option>
											</select>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Contact Details Tab -->
						<div v-if="activeTab === 'contact-details'" class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Contact Information</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Mobile</label>
											<input type="tel" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Personal Email</label>
											<input type="email" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Company Email</label>
											<input type="email" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Provide Email Address registered in company" />
										</div>
									</div>
								</div>
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Emergency Contact</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Emergency Contact Name</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Emergency Phone</label>
											<input type="tel" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Relation</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Office Use Tab -->
						<div v-if="activeTab === 'office-use'" class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Employment Details</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Date of Joining</label>
											<input type="date" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Employment Type</label>
											<select class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
												<option>Full-time</option>
												<option>Part-time</option>
												<option>Contract</option>
												<option>Intern</option>
											</select>
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Probation Period</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
									</div>
								</div>
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Work Details</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Shift</label>
											<select class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
												<option>Day Shift</option>
												<option>Night Shift</option>
												<option>Rotating</option>
											</select>
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Work Location</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Banking Tab -->
						<div v-if="activeTab === 'banking'" class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Bank Account Details</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Bank Name</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Account Number</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">IFSC Code</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
									</div>
								</div>
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Salary Information</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">CTC</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Salary Mode</label>
											<select class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
												<option>Bank Transfer</option>
												<option>Cash</option>
												<option>Check</option>
											</select>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- ID Proofs Tab -->
						<div v-if="activeTab === 'id-proofs'" class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Government IDs</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">PAN Number</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Aadhaar Number</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Passport Number</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
									</div>
								</div>
								<div class="space-y-4">
									<h3 class="text-lg font-medium text-gray-900">Other Documents</h3>
									<div class="space-y-3">
										<div>
											<label class="block text-sm font-medium text-gray-700">Driving License</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700">Voter ID</label>
											<input type="text" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" />
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- Documentation Tab -->
						<div v-if="activeTab === 'documentation'" class="space-y-6">
							<div class="space-y-4">
								<h3 class="text-lg font-medium text-gray-900">Documents</h3>
								<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
									<div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
										<div class="text-gray-400 mb-2">
											<svg class="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
												<path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
											</svg>
										</div>
										<div class="text-sm text-gray-600">
											<label class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
												<span>Upload Document</span>
												<input type="file" class="sr-only" />
											</label>
										</div>
									</div>
									<div class="bg-gray-50 rounded-lg p-4">
										<h4 class="font-medium text-gray-900">Resume</h4>
										<p class="text-sm text-gray-500">Upload your latest resume</p>
									</div>
									<div class="bg-gray-50 rounded-lg p-4">
										<h4 class="font-medium text-gray-900">Offer Letter</h4>
										<p class="text-sm text-gray-500">Company offer letter</p>
									</div>
								</div>
							</div>
						</div>

						<!-- Social Tab -->
						<div v-if="activeTab === 'social'" class="space-y-6">
							<div class="space-y-4">
								<h3 class="text-lg font-medium text-gray-900">Social – Your Vibe Hub</h3>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
									<div class="space-y-4">
										<h4 class="text-md font-medium text-gray-800">Professional Networks</h4>
										<div class="space-y-3">
											<div>
												<label class="block text-sm font-medium text-gray-700">LinkedIn Profile</label>
												<input type="url" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" placeholder="https://linkedin.com/in/..." />
											</div>
											<div>
												<label class="block text-sm font-medium text-gray-700">GitHub Profile</label>
												<input type="url" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" placeholder="https://github.com/..." />
											</div>
										</div>
									</div>
									<div class="space-y-4">
										<h4 class="text-md font-medium text-gray-800">Interests & Hobbies</h4>
										<div class="space-y-3">
											<div>
												<label class="block text-sm font-medium text-gray-700">Skills & Interests</label>
												<textarea rows="3" class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Share your skills, interests, and hobbies..."></textarea>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { ref, computed, inject } from "vue"
import BaseLayout from "@/components/BaseLayout.vue"

const __ = inject("$translate")

// Sample employee data - replace with actual data from your API
const employee = ref({
	name: "Vishal",
	employee_id: "HR-EMP-00001",
	status: "Active",
	department: "Engineering",
	designation: "Software Developer",
	branch: "Main Office"
})

// Tab configuration with the new order you requested
const tabs = [
	{ id: 'overview', label: 'Overview' },
	{ id: 'personal-details', label: 'Personal Details' },
	{ id: 'contact-details', label: 'Contact Details' },
	{ id: 'office-use', label: 'Office Use' },
	{ id: 'banking', label: 'Banking' },
	{ id: 'id-proofs', label: 'ID Proofs' },
	{ id: 'documentation', label: 'Documentation' },
	{ id: 'social', label: 'Social – Your Vibe Hub' }
]

const activeTab = ref('overview')

// Compute employee initials for avatar
const employeeInitials = computed(() => {
	if (!employee.value.name) return '?'
	return employee.value.name.split(' ').map(n => n[0]).join('').toUpperCase()
})
</script>
