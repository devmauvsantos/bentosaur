class_name BentosaurSaveStore
extends RefCounted

const SAVE_PATH := "user://bentosaur_save_v1.cfg"
const SAVE_SECTION := "progress"
const TOTAL_COINS_KEY := "total_coins"


static func load_total_coins() -> int:
	var config := ConfigFile.new()
	if config.load(SAVE_PATH) != OK:
		return 0
	return maxi(int(config.get_value(SAVE_SECTION, TOTAL_COINS_KEY, 0)), 0)


static func save_total_coins(total_coins: int) -> Error:
	var config := ConfigFile.new()
	config.set_value(SAVE_SECTION, TOTAL_COINS_KEY, maxi(total_coins, 0))
	return config.save(SAVE_PATH)
