<div align="center">
	<div class="flex items-center justify-center gap-3 mb-4">
		<!-- Abstract Logo with three intertwined ribbon shapes -->
		<div class="relative w-12 h-12">
			<!-- Top ribbon (pink) -->
			<svg class="absolute inset-0 w-full h-full" viewBox="0 0 48 48" fill="none">
				<path
					d="M12 24 Q24 16 36 24 Q30 32 24 40 Q18 32 12 24 Z"
					fill="#FF69B4"
					opacity="0.9"
				/>
			</svg>
			<!-- Middle ribbon (green) -->
			<svg class="absolute inset-0 w-full h-full" viewBox="0 0 48 48" fill="none">
				<path
					d="M9 27 Q24 21 39 27 Q33 33 24 39 Q15 33 9 27 Z"
					fill="#32CD32"
					opacity="0.8"
				/>
			</svg>
			<!-- Bottom ribbon (blue) -->
			<svg class="absolute inset-0 w-full h-full" viewBox="0 0 48 48" fill="none">
				<path
					d="M6 30 Q24 24 42 30 Q36 36 24 42 Q12 36 6 30 Z"
					fill="#4169E1"
					opacity="0.7"
				/>
			</svg>
		</div>
		
		<!-- Text "Shreyas" -->
		<div class="flex flex-col">
			<span class="text-3xl font-bold text-pink-500 italic">Shreyas</span>
			<div class="w-full h-1 bg-gray-300"></div>
		</div>
	</div>
	<h2>Shreyas HR</h2>
	<p align="center">
		<p>Open Source, modern, and easy-to-use HR and Payroll Software</p>
	</p>

[![CI](https://github.com/frappe/hrms/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/frappe/hrms/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/frappe/hrms/branch/develop/graph/badge.svg?token=0TwvyUg3I5)](https://codecov.io/gh/frappe/hrms)

<a href="https://trendshift.io/repositories/10972" target="_blank"><img src="https://trendshift.io/api/badge/repositories/10972" alt="frappe%2Fhrms | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</div>

<div align="center">
	<img src=".github/hrms-hero.png"/>
</div>

<div align="center">
	<a href="https://github.com/frappe/hrms">GitHub</a>
	-
	<a href="https://docs.frappe.io/hr/introduction">Documentation</a>
</div>

## Shreyas HR

Shreyas HR has everything you need to drive excellence within the company. It's a complete HRMS solution with over 13 different modules right from Employee Management, Onboarding, Leaves, to Payroll, Taxation, and more!

## Motivation
When Frappe team started growing in terms of size, we needed an open-source HR and Payroll software. We didn't find any "true" open-source HR software out there and so decided to build one ourselves.
Initially, it was a set of modules within ERPNext but version 14 onwards, as the modules became more mature, Shreyas HR was created as a separate product.

## Key Features

- **Employee Lifecycle**: From onboarding employees, managing promotions and transfers, all the way to documenting feedback with exit interviews, make life easier for employees throughout their life cycle.
- **Leave and Attendance**: Configure leave policies, pull regional holidays with a click, check-in and check-out with geolocation capturing, track leave balances and attendance with reports.
- **Expense Claims and Advances**: Manage employee advances, claim expenses, configure multi-level approval workflows, all this with seamless integration with modern accounting systems.
- **Performance Management**: Track goals, align goals with key result areas (KRAs), enable employees to evaluate themselves, make managing appraisal cycles easy.
- **Payroll & Taxation**: Create salary structures, configure income tax slabs, run standard payroll, accomodate additional salaries and off cycle payments, view income breakup on salary slips and so much more.
- **Shreyas HR Mobile App**: Apply for and approve leaves on the go, check-in and check-out, access employee profile right from the mobile app.

<details open>

<summary>View Screenshots</summary>
	<img src=".github/hrms-appraisal.png"/>
	<img src=".github/hrms-requisition.png"/>
	<img src=".github/hrms-attendance.png"/>
	<img src=".github/hrms-salary.png"/>
	<img src=".github/hrms-pwa.png"/>
</details>

### Under the Hood

- [**Frappe Framework**](https://github.com/frappe/frappe): A full-stack web application framework written in Python and Javascript. The framework provides a robust foundation for building web applications, including a database abstraction layer, user authentication, and a REST API.

- [**Frappe UI**](https://github.com/frappe/frappe-ui): A Vue-based UI library, to provide a modern user interface. The Frappe UI library provides a variety of components that can be used to build single-page applications on top of the Frappe Framework.

## Production Setup

### Managed Hosting

You can try [Frappe Cloud](https://frappecloud.com), a simple, user-friendly and sophisticated [open-source](https://github.com/frappe/press) platform to host Frappe applications with peace of mind.

It takes care of installation, setup, upgrades, monitoring, maintenance and support of your Frappe deployments. It is a fully featured developer platform with an ability to manage and control multiple Frappe deployments.

<div>
	<a href="https://frappecloud.com/hrms/signup" target="_blank">
		<picture>
			<source media="(prefers-color-scheme: dark)" srcset="https://frappe.io/files/try-on-fc-white.png">
			<img src="https://frappe.io/files/try-on-fc-black.png" alt="Try on Frappe Cloud" height="28" />
		</picture>
	</a>
</div>


## Development setup
### Docker
You need Docker, docker-compose and git setup on your machine. Refer [Docker documentation](https://docs.docker.com/). After that, run the following commands:
```
git clone https://github.com/frappe/hrms
cd hrms/docker
docker-compose up
```

Wait for some time until the setup script creates a site. After that you can access `http://localhost:8000` in your browser and the login screen for HR should show up.

Use the following credentials to log in:

- Username: `Administrator`
- Password: `admin`

### Local

1. Set up bench by following the [Installation Steps](https://frappeframework.com/docs/user/en/installation) and start the server and keep it running
	```sh
	$ bench start
	```
2. In a separate terminal window, run the following commands
	```sh
	$ bench new-site hrms.local
	# $ bench get-app erpnext  # ERPNext removed - HRMS only
	$ bench get-app hrms
	$ bench --site hrms.local install-app hrms
	$ bench --site hrms.local add-to-hosts
	```
3. You can access the site at `http://hrms.local:8080`

## Learning and Community

1. [Frappe School](https://frappe.school) - Learn Frappe Framework from the various courses by the maintainers or from the community.
2. [Documentation](https://docs.frappe.io/hr) - Extensive documentation for Frappe HR.
3. [User Forum](https://discuss.frappe.io/) - Engage with the community of Frappe users and service providers.
4. [Telegram Group](https://t.me/frappehr) - Get instant help from the community of users.


## Contributing

1. [Issue Guidelines](https://github.com/frappe/hrms/wiki/Issue-Guidelines)
2. [Report Security Vulnerabilities](https://frappe.io/security)
3. [Pull Request Requirements](https://github.com/frappe/hrms/wiki/Contribution-Guidelines)


## Logo and Trademark Policy

Please read our [Logo and Trademark Policy](TRADEMARK_POLICY.md).

<br />
<br />
<div align="center" style="padding-top: 0.75rem;">
	<a href="https://frappe.io" target="_blank">
		<picture>
			<source media="(prefers-color-scheme: dark)" srcset="https://frappe.io/files/Frappe-white.png">
			<img src="https://frappe.io/files/Frappe-black.png" alt="Frappe Technologies" height="28"/>
		</picture>
	</a>
</div>

