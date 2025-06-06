import { ref } from "vue";

export type NavigationCallback = (item: NavigationItem) => void;

//object for navigation in wizard
export interface StepsNavigationItem {
	name: string;
	id: string;
	tag: string;
	current: boolean;
	status: string;
	show: boolean;
}
export interface NavigationItem {
	name: string;
	tag: string;
	current: boolean;
	show: boolean;
}

export const otpUri = ref("");
export const secret = ref("");
export const scratchCodes = ref<string[]>([]);
export const codeGenrated = ref(false);
export const loaded = ref(false);
export const generateQrBtnClicked = ref(false);
export const userInput = ref("");
export const accountName = ref("");
export const modalTitle = ref("Default Title");
export const modalMessage = ref("Default message.");
export const confirmText = ref("Continue");
export const showModal = ref(false);
export const fileGenerated = ref(false);
export const verified = ref(false);

export function reset2FAState() {
	otpUri.value = "";
	secret.value = "";
	scratchCodes.value = [];
	codeGenrated.value = false;
	loaded.value = true;
	generateQrBtnClicked.value = false;
	userInput.value = "";
	accountName.value = "";
	modalTitle.value = "Default Title";
	modalMessage.value = "Default message.";
	confirmText.value = "Continue";
	showModal.value = false;
	fileGenerated.value = false;
	verified.value = false;
  }