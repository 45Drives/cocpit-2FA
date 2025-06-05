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
