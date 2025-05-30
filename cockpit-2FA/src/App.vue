<template>
	<div class="min-h-screen h-full w-full min-w-fit flex flex-col bg-default overflow-auto">
		<HoustonAppContainer moduleName="2 FA" :appVersion="version"  >
<Home></Home>
		</HoustonAppContainer>
	</div>
</template>

<script setup lang="ts">
// import "@45drives/houston-common-ui/style.css";
import '../../houston-common/houston-common-ui/dist/style.css';
import '@45drives/houston-common-css/src/index.css';
import { HoustonAppContainer } from "@45drives/houston-common-ui";

import Home from './views/Home.vue';
const version = __APP_VERSION__;

</script>

	