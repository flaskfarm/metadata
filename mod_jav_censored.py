from urllib.parse import urlparse
from flask import send_from_directory
from support_site import (
    SiteDmm,
    SiteAvdbs,
    SiteHentaku,
    SiteJav321,
    SiteJavbus,
    SiteMgstage,
    SiteUtilAv as SiteUtil,
    SiteJavdb,
    UtilNfo,
    DiscordUtil
)
from .setup import *
from support import d

class ModuleJavCensored(PluginModuleBase):
    
    def __init__(self, P):
        super(ModuleJavCensored, self).__init__(P, name='jav_censored', first_menu='setting')
        self.site_map = {
            "avdbs": SiteAvdbs,
            "dmm": SiteDmm,
            "hentaku": SiteHentaku,
            "jav321": SiteJav321,
            "javbus": SiteJavbus,
            "mgstage": SiteMgstage,
            "javdb": SiteJavdb,
        }

        self.db_default = {
            f"{self.name}_db_version": "1",
            f"{self.name}_order": "dmm, mgstage, jav321, javdb, javbus",
            f"{self.name}_actor_order": "avdbs",
            f"{self.name}_result_priority_order": "dmm_videoa, mgstage, dmm_dvd, dmm_bluray, dmm_unknown, jav321, javdb, javbus",

            # 공통 설정
            f"{self.name}_trans_option": "using",  #"not_using" 사용안함, "using" 내장기본구글web2, "using_plugin":번역플러그인
            f"{self.name}_title_format": "[{title}] {tagline}",
            f"{self.name}_art_count": "0",
            f"{self.name}_tag_option": "not_using", # not_using, label, label_and_site, site
            f"{self.name}_use_extras": "False",

            # 이미지 모드
            # 3개로 정리ff_proxy, discord_proxy, image_server
            f"{self.name}_image_mode": "ff_proxy", 

            # 디스코드 프록시 서버 관련 설정
            f"{self.name}_use_discord_proxy_server": "False",
            f"{self.name}_discord_proxy_server_url": "",
            f"{self.name}_use_my_webhook": "False",
            f"{self.name}_my_webhook_list": "",

            # 이미지 서버
            f"{self.name}_image_server_url": f"{F.SystemModelSetting.get('ddns')}/images",
            f"{self.name}_image_server_local_path": "/data/images",
            f"{self.name}_image_server_save_format": "/jav/cen/{label_1}/{label}",
            
            # avdbs
            f"{self.name}_avdbs_use_proxy": "False",
            f"{self.name}_avdbs_proxy_url": "",
            f"{self.name}_avdbs_use_local_db": "True",
            f"{self.name}_avdbs_local_db_path": f"{PLUGIN_ROOT}/files/jav_actors2.db",
            "jav_actor_img_url_prefix": "",
            f"{self.name}_avdbs_test_name": "",

            # hentaku
            f"{self.name}_hentaku_use_proxy": "False",
            f"{self.name}_hentaku_proxy_url": "",
            f"{self.name}_hentaku_test_name": "",

            # dmm
            f"{self.name}_dmm_use_proxy": "False",
            f"{self.name}_dmm_proxy_url": "",
            f"{self.name}_dmm_parser_type0_rules": "^\\d(3dsvr)(\\d+)$=>1=>2",
            f"{self.name}_dmm_parser_type1_labels": "AP, GOOD, SAN, TEN",
            f"{self.name}_dmm_parser_type2_labels": "ID",
            f"{self.name}_dmm_parser_type3_labels": "AP, ID, NTRD, SAN, SORA, SW, TEN",
            f"{self.name}_dmm_parser_type4_labels": "",
            f"{self.name}_dmm_small_image_to_poster": "",
            f"{self.name}_dmm_crop_mode": "",
            f"{self.name}_dmm_priority_search_labels": "",
            f"{self.name}_dmm_test_code": "ssni-900",

            # mgstage
            f"{self.name}_mgstage_use_sjva": "False",
            f"{self.name}_mgstage_use_proxy": "False",
            f"{self.name}_mgstage_proxy_url": "",
            f"{self.name}_mgstage_small_image_to_poster": "",
            f"{self.name}_mgstage_crop_mode": "",
            f"{self.name}_mgstage_priority_search_labels": "",
            f"{self.name}_mgstage_maintain_series_number_labels": "GOOD, TEN",
            f"{self.name}_mgstage_test_code": "abf-010",

            # jav321
            #f"{self.name}_jav321_use_sjva": "False",
            f"{self.name}_jav321_use_proxy": "False",
            f"{self.name}_jav321_proxy_url": "",
            f"{self.name}_jav321_small_image_to_poster": "",
            f"{self.name}_jav321_crop_mode": "",
            f"{self.name}_jav321_priority_search_labels": "",
            f"{self.name}_jav321_maintain_series_number_labels": "AP, GOOD, ID, NTRD, SAN, SORA, SW, TEN",
            f"{self.name}_jav321_test_code": "abw-354",

            # javdb
            f"{self.name}_javdb_use_sjva": "False",
            f"{self.name}_javdb_use_proxy": "False",
            f"{self.name}_javdb_proxy_url": "",
            f"{self.name}_javdb_small_image_to_poster": "",
            f"{self.name}_javdb_crop_mode": "",
            f"{self.name}_javdb_priority_search_labels": "",
            f"{self.name}_javdb_maintain_series_number_labels": "AP, GOOD, ID, NTRD, SAN, SORA, SW, TEN",
            f"{self.name}_javdb_test_code": "JUFE-487",

            # javbus
            f"{self.name}_javbus_use_sjva": "False",
            f"{self.name}_javbus_use_proxy": "False",
            f"{self.name}_javbus_proxy_url": "",
            f"{self.name}_javbus_small_image_to_poster": "",
            f"{self.name}_javbus_crop_mode": "",
            f"{self.name}_javbus_priority_search_labels": "",
            f"{self.name}_javbus_maintain_series_number_labels": "AP, GOOD, ID, NTRD, SAN, SORA, SW, TEN",
            f"{self.name}_javbus_test_code": "abw-354",
        }
        
        try:
            self.keyword_cache = F.get_cache(f"{P.package_name}_{self.name}_keyword_cache")
        except Exception as e:
            self.keyword_cache = {}

    ################################################
    # region PluginModuleBase 메서드 오버라이드

    def plugin_load(self):
        self.__set_site_setting()
    
    def plugin_load_celery(self):
        self.__set_site_setting()
    
    # 사이트 설정값이 바뀌면 config
    def setting_save_after(self, change_list):
        ins_list = []
        
        always_all_set = [
            "jav_censored_use_extras",
            "jav_censored_art_count", 
            #"jav_censored_image_server_url",
            #"jav_censored_image_server_local_path",
            #"jav_censored_use_discord_proxy_server",
            #"jav_censored_discord_proxy_server_url"
        ]
        # 굳이???? 
        for tmp in always_all_set:
            if tmp in change_list:
                ins_list = list(self.site_map.values())
                break
            if ins_list:
                break
        
        if True:
            for key in change_list:
                if key.endswith("_test_code"):
                    continue
                for site, ins in self.site_map.items():
                    if site in key:
                        if ins not in ins_list:
                            ins_list.append(ins)
                            break
        self.__set_site_setting(ins_list)

    def __set_site_setting(self, ins_list=None):
        if ins_list is None:
            ins_list = self.site_map.values()
        for ins in ins_list:
            try:
                P.logger.debug(f"set_config site {ins.__name__} with settings.")
                ins.set_config(P.ModelSetting)
            except Exception as e:
                P.logger.error(f"Error initializing site {ins}: {str(e)}")
                #P.logger.error(traceback.format_exc())
   

    def process_command(self, command, arg1, arg2, arg3, req):
        try:
            ret = {'ret': 'success'}
            if command == "test":
                code = arg2
                call = arg1 # 'dmm', 'mgstage', 'javbus' 등
                db_prefix = f"{self.name}_{call}"
                P.ModelSetting.set(f"{db_prefix}_test_code", code)

                current_site_settings = self.__site_settings(call)
                logger.debug(f"process_ajax (test, call='{call}'): current_site_settings['proxy_url'] = {current_site_settings.get('proxy_url')}")

                search_results = self.search2(code, call, manual=True, site_settings_override=current_site_settings)

                if not search_results:
                    ret['ret'] = "warning"
                    ret['msg'] = f"no results for '{code}'"
                    return jsonify(ret)

                info_data = self.info(search_results[0]['code'], keyword=code)
                ret['json'] = {
                    "search": search_results,
                    "info": info_data if info_data else {}
                }
                
                # 2025.07.11 by soju6jan 임시 코드
                # javdb poster pil 객체로 리턴됨.
                try:
                    if call == "javdb":
                        if isinstance(ret['json']['info']['thumb'][0]
                        ['value'], str) == False:
                            ret['json']['info']['thumb'][0]['value'] = "이미지객체"
                except Exception as e: pass

                return jsonify(ret)
            elif command == "actor_test":
                name = arg2
                call = arg1 # 'avdbs' 또는 'hentaku'
                db_prefix = f"{self.name}_{call}"
                P.ModelSetting.set(f"{db_prefix}_test_name", name)

                entity_actor = {"originalname": name}
                sett = self.__site_settings(call)

                if call == 'avdbs':
                    sett['use_local_db'] = P.ModelSetting.get_bool('jav_censored_avdbs_use_local_db')
                    sett['local_db_path'] = P.ModelSetting.get('jav_censored_avdbs_local_db_path')
                    sett['db_image_base_url'] = P.ModelSetting.get('jav_actor_img_url_prefix')
                    sett['site_name_for_db_query'] = call

                # Hentaku에 대한 특별한 설정이 있다면 여기에 추가
                # elif call == 'hentaku':
                #    pass

                SiteClass = self.site_map.get(call)
                if SiteClass:
                    logger.debug(f"Actor Test: Calling {SiteClass.__name__}.get_actor_info with sett: {sett}")
                    if SiteClass in [SiteAvdbs]:
                        SiteClass.get_actor_info(entity_actor)
                    else:
                        # hentaku 동작하지 않음.
                        pass
                        #SiteClass.get_actor_info(entity_actor, **sett)
                else:
                    logger.error(f"Actor Test: Cannot find SiteClass for call='{call}'")
                    entity_actor['error'] = f"Site class for '{call}' not found."
                ret['title'] = f"{arg2} 검색결과"
                ret['json'] = entity_actor
                #return jsonify(entity_actor)
            elif command == "rcache_clear":
                SiteUtil.session.cache.clear()
                return jsonify({"msg": "초기화 성공"})
            return jsonify(ret)
        except Exception as e:
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())
            return jsonify({'ret':'exception', 'log':str(e)})

    def process_api(self, sub, req):
        call = req.args.get("call", "")
        if sub == "search" and call in ["plex", "kodi"]:
            keyword = req.args.get("keyword").rstrip("-").strip()
            manual = req.args.get("manual") == "True"
            return jsonify(self.search(keyword, manual=manual))
        if sub == "info":
            data = self.info(req.args.get("code"))
            if call == "kodi":
                data = SiteUtil.info_to_kodi(data)
            return jsonify(data)
        return None

    def process_normal(self, sub, req):
        if sub == "nfo_download":
            keyword = req.args.get("code")
            call = req.args.get("call")
            if call in self.site_map:
                db_prefix = f"{self.name}_{call}"
                P.ModelSetting.set(f"{db_prefix}_test_code", keyword)
                
                # NFO 다운로드도 search -> info 흐름을 따름
                search_results = self.search2(keyword, call)
                if search_results:
                    self.keyword_cache.set(search_results[0]['code'], keyword) # 수동 캐싱
                    info = self.info(search_results[0]["code"])
                    if info:
                        return UtilNfo.make_nfo_movie(info, output="file", filename=info["originaltitle"].upper() + ".nfo")
        return None

    # endregion PluginModuleBase 메서드 오버라이드
    ################################################     


    ################################################
    # region SEARCH

    def search(self, keyword, manual=False):
        logger.debug(f"======= jav censored search START - keyword:[{keyword}] manual:[{manual}] =======")
        #self.keyword_cache = {}
        all_results = []
        original_site_order_list = P.ModelSetting.get_list(f"{self.name}_order", ",") # 설정된 기본 사이트 순서
        
        # --- 1. 현재 검색어의 대표 레이블 추출 ---
        current_keyword_label = ""
        if keyword and '-' in keyword:
            current_keyword_label = keyword.split('-', 1)[0].upper()
        elif keyword: 
            match_kw_label = re.match(r'^([A-Z]+)', keyword.upper())
            if match_kw_label: current_keyword_label = match_kw_label.group(1)
        
        # --- is_keyword_potentially_priority_for_any_site 플래그 계산 ---
        is_keyword_potentially_priority_for_any_site = False
        if current_keyword_label: # 대표 레이블이 추출되었을 때만 확인
            # 모든 사이트의 "지정 레이블 최우선" 설정을 순회
            for site_key_for_potential_check in self.site_map.keys(): # site_map에 등록된 모든 사이트
                # 실제로는 original_site_order_list를 순회하는 것이 더 효율적일 수 있으나, 모든 가능성을 보려면 site_map 사용
                db_prefix_potential = f"{self.name}_{site_key_for_potential_check}"
                priority_labels_str_potential = P.ModelSetting.get(f"{db_prefix_potential}_priority_search_labels")
                if priority_labels_str_potential:
                    site_priority_labels_set_potential = {lbl.strip().upper() for lbl in priority_labels_str_potential.split(',') if lbl.strip()}
                    if current_keyword_label in site_priority_labels_set_potential:
                        is_keyword_potentially_priority_for_any_site = True
                        logger.debug(f"  Potential Priority: Keyword label '{current_keyword_label}' is a priority for site '{site_key_for_potential_check}'.")
                        break # 하나라도 찾으면 더 이상 확인할 필요 없음
            if is_keyword_potentially_priority_for_any_site:
                logger.debug(f"Keyword label '{current_keyword_label}' is potentially a priority label for at least one site. 조기 종료 조건이 이에 따라 조정됩니다.")
        
        special_priority_site = None # 이 검색어에 대해 특별히 우선 검색할 사이트
        if current_keyword_label:
            logger.debug(f"Search keyword: '{keyword}', Extracted keyword label: '{current_keyword_label}' for dynamic site ordering.")
            # original_site_order_list 순서대로 각 사이트의 우선 레이블 설정을 확인
            for site_key_check_priority in original_site_order_list:
                if site_key_check_priority not in self.site_map: continue
                
                db_prefix_check = f"{self.name}_{site_key_check_priority}"
                priority_labels_str = P.ModelSetting.get(f"{db_prefix_check}_priority_search_labels")
                if priority_labels_str:
                    site_priority_labels_set = {lbl.strip().upper() for lbl in priority_labels_str.split(',') if lbl.strip()}
                    if current_keyword_label in site_priority_labels_set:
                        special_priority_site = site_key_check_priority
                        logger.debug(f"Keyword label '{current_keyword_label}' is a priority for site '{special_priority_site}'. This site will be searched first.")
                        break # 첫 번째로 매칭되는 우선 지정 사이트를 찾으면 중단
        
        # --- 2. 검색 순서 동적 조정 ---
        site_list_for_current_search = list(original_site_order_list) # 복사본 사용
        if special_priority_site and special_priority_site in site_list_for_current_search:
            site_list_for_current_search.remove(special_priority_site)
            site_list_for_current_search.insert(0, special_priority_site)
            logger.debug(f"Dynamically adjusted site search order: {site_list_for_current_search}")
        else:
            logger.debug(f"Using default site search order: {site_list_for_current_search}")

        # --- 기존 조기 종료 관련 설정 ---
        priority_sites_for_general_early_exit = { # 일반 조기 종료 대상
            "dmm": ["videoa",],
            "mgstage": True 
        }
        early_exit_triggered = False

        # --- 3. 각 사이트 검색 (조정된 순서 또는 기본 순서 사용) ---
        for site_key_in_order in site_list_for_current_search: # 조정된 순서 사용
            if early_exit_triggered: break

            if site_key_in_order not in self.site_map: continue # 이 부분은 위에서 이미 처리 가능
            logger.debug(f"--- Searching on site: {site_key_in_order} (Effective Order) ---")
            
            # current_site_settings에는 priority_label_setting_str이 포함됨 (__site_settings에서 설정)
            current_site_settings = self.__site_settings(site_key_in_order)
            
            data_from_search2 = self.search2(keyword, site_key_in_order, manual=manual, site_settings_override=current_site_settings)

            if data_from_search2: 
                logger.debug(f"  Got {len(data_from_search2)} result(s) from {site_key_in_order}")
                for item_result_dict in data_from_search2: 
                    item_result_dict['original_score'] = item_result_dict.get("score", 0)
                    item_result_dict['site_key'] = item_result_dict.get("site_key", site_key_in_order)
                    item_result_dict['hq_poster_passed'] = False
                    if 'is_priority_label_site' not in item_result_dict:
                        item_result_dict['is_priority_label_site'] = False
                    if 'code' in item_result_dict:
                        self.keyword_cache.set(item_result_dict['code'], keyword)

                    all_results.append(item_result_dict)

                    # --- 자동 검색 시 조기 종료 로직 ---
                    if not manual and item_result_dict['original_score'] == 100:
                        current_item_site = item_result_dict.get('site_key')
                        current_item_type = item_result_dict.get('content_type')
                        is_this_item_priority_label_match = item_result_dict.get('is_priority_label_site', False)

                        allow_general_early_exit = False
                        site_early_exit_config = priority_sites_for_general_early_exit.get(current_item_site)
                        if site_early_exit_config is True: allow_general_early_exit = True
                        elif isinstance(site_early_exit_config, list) and current_item_type in site_early_exit_config: allow_general_early_exit = True
                        
                        if allow_general_early_exit:
                            # 특별 우선 검색 대상 사이트에서 "지정 레이블" 매칭된 100점 결과가 나왔다면, 즉시 조기 종료.
                            if current_item_site == special_priority_site and is_this_item_priority_label_match:
                                logger.info(f"PRIORITY LABEL match (100-score) found on its designated priority site '{current_item_site}'. Activating early exit for '{keyword}'.")
                                early_exit_triggered = True
                                break
                            # 특별 우선 검색 대상 사이트가 아니거나, 또는 지정 레이블 매칭이 아닌 일반 100점일 경우,
                            # 그리고 이 검색어 레이블이 다른 사이트에서 우선 지정되지 "않았을" 때만 조기 종료.
                            elif not is_keyword_potentially_priority_for_any_site:
                                logger.info(f"General 100-score match from '{current_item_site}' (type: {current_item_type}). Activating early exit for '{keyword}'. (Keyword not a priority label for other sites)")
                                early_exit_triggered = True
                                break
                            elif is_keyword_potentially_priority_for_any_site and not is_this_item_priority_label_match:
                                logger.info(f"General 100-score match from '{current_item_site}' (type: {current_item_type}). Keyword IS a priority for other sites. Continuing search.")

            if early_exit_triggered:
                logger.debug("  Early exit triggered. Stopping further site searches.")
                break

        logger.debug(f"--- All site searches completed. Total initial results: {len(all_results)} ---")
        if not all_results:
            logger.debug("======= jav censored search END - No results found. =======")
            return []

        # 2단계: HQ 포스터 검증 (manual=False 일 때)
        if not manual and all_results:
            logger.debug("--- Starting HQ Poster check ---")
            all_results_sorted_for_hq_check = sorted(all_results, key=lambda k: k.get("original_score", 0), reverse=True)

            if all_results_sorted_for_hq_check: 
                top_original_score = all_results_sorted_for_hq_check[0].get("original_score", 0)
                score_threshold = 95

                if top_original_score >= score_threshold:
                    candidates_for_hq_check = [
                        item for item in all_results_sorted_for_hq_check 
                        if item.get("original_score", 0) >= score_threshold
                    ]
                    logger.debug(f"HQ Check: {len(candidates_for_hq_check)} candidates (score >= {score_threshold}).")

                    for candidate_item_ref in candidates_for_hq_check:
                        item_in_all_results_to_update = next(
                            (
                                x for x in all_results 
                                if x.get('code') == candidate_item_ref.get('code') and 
                                   x.get('site_key') == candidate_item_ref.get('site_key')
                            ),
                            None
                        )

                        if not item_in_all_results_to_update:
                            logger.warning(f"HQ Check: Could not find original item in all_results for candidate code {candidate_item_ref.get('code')}. Skipping HQ check for this item.")
                            continue

                        code_for_hq_check = item_in_all_results_to_update.get("code")
                        site_key_for_hq_check = item_in_all_results_to_update.get("site_key")
                        ps_url_for_hq_check = candidate_item_ref.get("image_url")

                        if not code_for_hq_check or not site_key_for_hq_check:
                            logger.warning(f"HQ Check: Code or site_key missing for an item. Skipping HQ check.")
                            continue

                        # --- hq_poster_score_adj 초기화 및 기본 페널티 설정 ---
                        item_in_all_results_to_update['hq_poster_score_adj'] = -1

                        try:
                            info_data_for_hq_check = self.info2(
                                code_for_hq_check, 
                                site_key_for_hq_check, 
                                keyword, 
                                ps_url=ps_url_for_hq_check
                            )

                            if info_data_for_hq_check:
                                ps_url_hq, pl_url_hq = None, None
                                for thumb_item_hq in info_data_for_hq_check.get('thumb', []):
                                    if thumb_item_hq.get('aspect') == 'poster': 
                                        ps_url_hq = thumb_item_hq.get('value')
                                    if thumb_item_hq.get('aspect') == 'landscape': 
                                        pl_url_hq = thumb_item_hq.get('value')
                                    if ps_url_hq and pl_url_hq: 
                                        break

                                if ps_url_hq and pl_url_hq:
                                    settings_for_hq_proxy = self.__site_settings(site_key_for_hq_check)
                                    proxy_url_for_hq_util = settings_for_hq_proxy.get("proxy_url")

                                    poster_pos_result = SiteUtil.has_hq_poster(ps_url_hq, pl_url_hq, proxy_url=proxy_url_for_hq_util)
                                    if poster_pos_result:
                                        logger.debug(f"HQ Check PASSED for {code_for_hq_check} on {site_key_for_hq_check}.")
                                        item_in_all_results_to_update['hq_poster_score_adj'] = 0
                                    else:
                                        logger.debug(f"HQ Check FAILED (has_hq_poster returned None) for {code_for_hq_check} on {site_key_for_hq_check}. Penalty: -1.")
                                else:
                                    logger.debug(f"HQ Check SKIPPED (ps_url or pl_url missing) for {code_for_hq_check} on {site_key_for_hq_check}. Penalty: -1.")
                            else:
                                logger.debug(f"HQ Check SKIPPED (info_data_for_hq is None) for {code_for_hq_check} on {site_key_for_hq_check}. Penalty: -1.")
                        except Exception as e_info_hq_check:
                            logger.error(f"HQ Check Exception for {code_for_hq_check} on {site_key_for_hq_check}: {e_info_hq_check}")
                            item_in_all_results_to_update['hq_poster_score_adj'] = -2 

        # 3단계: 조정된 점수 계산
        for item_adj_score in all_results:
            item_adj_score['adjusted_score'] = item_adj_score.get('original_score', 0) + item_adj_score.get('hq_poster_score_adj', 0)

        # 4단계: 사용자 정의 우선순위에 따른 정렬
        # logger.debug("--- Starting Custom Priority Sort ---")
        priority_string = P.ModelSetting.get('jav_censored_result_priority_order')
        priority_list = [x.strip() for x in priority_string.split(',') if x.strip()]
        dynamic_priority_map = {key: index for index, key in enumerate(priority_list)}
        lowest_priority = len(priority_list)

        def get_priority_value_for_sort(item_to_sort):
            site_key_prio = item_to_sort.get('site_key')
            content_type_prio = item_to_sort.get('content_type')
            calculated_prio = lowest_priority
            if site_key_prio == 'dmm' and content_type_prio:
                type_specific_key = f"dmm_{content_type_prio}"
                calculated_prio = dynamic_priority_map.get(type_specific_key, lowest_priority)
            if calculated_prio >= lowest_priority: 
                calculated_prio = dynamic_priority_map.get(site_key_prio, lowest_priority)
            return calculated_prio

        def get_custom_sort_key_for_final(item_for_final_sort):
            # 1. 지정 레이블 우선 플래그 (True=0, False=1 -> True가 더 먼저 오도록)
            label_prio_flag_sort_val = 0 if item_for_final_sort.get('is_priority_label_site') else 1

            # 2. 조정된 점수 (내림차순)
            adj_score = -item_for_final_sort.get("adjusted_score", 0) 

            # 3. 일반 우선순위 (jav_censored_result_priority_order 값, 오름차순)
            prio_val = get_priority_value_for_sort(item_for_final_sort) # 기존 함수 호출

            return (label_prio_flag_sort_val, adj_score, prio_val)

        # 5단계: 사용자 정의 우선순위에 따른 정렬
        # logger.debug("--- Starting Custom Priority Sort (with Label Priority Flag) ---")
        # for i, item_debug in enumerate(all_results):
        #    label_prio_val_debug = 0 if item_debug.get('is_priority_label_site') else 1
        #    adj_score_debug = -item_debug.get("adjusted_score", 0)
        #    prio_val_debug = get_priority_value_for_sort(item_debug)
        #    logger.debug(f"    Item {i}: Code={item_debug.get('code')}, Site={item_debug.get('site_key')}, PrioLabelFlag={item_debug.get('is_priority_label_site')}, SortKey=({label_prio_val_debug}, {adj_score_debug}, {prio_val_debug})")

        sorted_results_after_priority = sorted(all_results, key=get_custom_sort_key_for_final)
        # logger.debug("--- Custom Priority Sort (with Label Priority Flag) END ---")

        # 6단계: "조정된 점수"가 같은 동점자 그룹 내에서, 최종 정렬 순서에 따라 페널티 적용
        # logger.debug("--- Starting Tie-Breaking Penalty and Final Score Assignment ---")
        if sorted_results_after_priority:
            last_adjusted_score_for_penalty_group = None 
            penalty_for_current_score_group = 0      

            for item_in_sorted_list in sorted_results_after_priority:
                
                current_adj_score = item_in_sorted_list.get('adjusted_score', 0)

                if current_adj_score != last_adjusted_score_for_penalty_group:
                    penalty_for_current_score_group = 0
                
                calculated_final_score = current_adj_score - penalty_for_current_score_group
                item_in_sorted_list['score'] = max(0, calculated_final_score)

                last_adjusted_score_for_penalty_group = current_adj_score
                penalty_for_current_score_group += 1

        # logger.debug("--- Tie-Breaking Penalty and Final Score Assignment END ---")

        final_results_to_return = sorted_results_after_priority

        if final_results_to_return: # 변수명 변경에 따른 로깅 수정
            logger.debug("Top results after final scoring:")
            for i, item_log_final_list in enumerate(final_results_to_return):
                logger.debug(f"  {i+1}. Final Score={item_log_final_list.get('score')}, AdjScore={item_log_final_list.get('adjusted_score')}, Site={item_log_final_list.get('site_key')}, Type={item_log_final_list.get('content_type')}, PrioLabel={item_log_final_list.get('is_priority_label_site', False)}, Code={item_log_final_list.get('code')}")

        logger.debug(f"======= jav censored search END - Returning {len(final_results_to_return)} results. =======")
        return final_results_to_return


    def search2(self, keyword, site, manual=False, site_settings_override=None):
        SiteClass = self.site_map.get(site, None)
        if SiteClass is None:
            return None
        sett = site_settings_override if site_settings_override is not None else self.__site_settings(site)
        try:
            # TODO
            if SiteClass in [SiteDmm, SiteJav321]:
                data = SiteClass.search(keyword, do_trans=manual, manual=manual) 
            else:    
                data = SiteClass.search(keyword, do_trans=manual, manual=manual, **sett) 
            if data and data.get("ret") == "success" and data.get("data"):
                if isinstance(data["data"], list) and data["data"]:
                    return data["data"]
                elif not isinstance(data["data"], list):
                    logger.warning(f"search2: Site '{site}' returned data that is not a list: {type(data['data'])}")
            # else: # 결과 없거나 실패 시 로그는 SiteClass.search 내부 또는 여기서 처리
            #    logger.debug(f"No valid results from {site} for '{keyword}'. Response: {data.get('ret') if data else 'None'}")
        except Exception as e_site_search:
            logger.error(f"Error during search on site '{site}' for keyword '{keyword}': {e_site_search}")
        return None

    # endregion SEARCH
    ################################################


    ################################################
    # region INFO

    def info(self, code, keyword=None):
        if code[1] == "B":
            site = "javbus"
        elif code[1] == "D":
            site = "dmm"
        elif code[1] == "T":
            site = "jav321"
        elif code[1] == "M":
            site = "mgstage"
        elif code[1] == "J":
            site = "javdb"
        else:
            logger.error("처리할 수 없는 코드: code=%s", code)
            return None

        if keyword is None:
            keyword = self.keyword_cache.get(code)
            if keyword:
                logger.debug(f"info: Found keyword '{keyword}' in cache for code '{code}'.")

        ret = self.info2(code, site, keyword)
        if ret is None:
            logger.debug(f"info2 returned None for code: {code}")
            return ret

        db_prefix = f"{self.name}_{site}"

        ret["plex_is_proxy_preview"] = True
        ret["plex_is_landscape_to_art"] = True
        ret["plex_art_count"] = len(ret.get("fanart", []))

        actors = ret.get("actor") or []
        actor_names_for_log = []
        if actors:
            for item in actors:
                self.process_actor(item)
                actor_names_for_log.append(item.get("name", item.get("originalname", "?")))

        for item in actors:
            self.process_actor(item)

            try:
                name_ja, name_ko = item.get("originalname"), item.get("name")
                if name_ja and name_ko:
                    name_trans = SiteUtil.trans(name_ja)
                    if name_trans != name_ko:
                        if ret.get("plot"): ret["plot"] = ret["plot"].replace(name_trans, name_ko)
                        if ret.get("tagline"): ret["tagline"] = ret["tagline"].replace(name_trans, name_ko)
                        for extra in ret.get("extras") or []:
                            if extra.get("title"): extra["title"] = extra["title"].replace(name_trans, name_ko)
            except Exception:
                logger.exception("오역된 배우 이름이 들어간 항목 수정 중 예외:")

        # 타이틀 포맷 적용 전 원본 타이틀 임시 저장 (로그용)
        original_calculated_title = ret.get("title", "")

        try: # 타이틀 포맷팅
            title_format = P.ModelSetting.get(f"{self.name}_title_format")
            format_dict = {
                'originaltitle': ret.get("originaltitle", ""),
                'plot': ret.get("plot", ""),
                'title': original_calculated_title, # 포맷팅 전 제목 사용
                'sorttitle': ret.get("sorttitle", ""),
                'runtime': ret.get("runtime", ""),
                'country': ', '.join(ret.get("country", [])),
                'premiered': ret.get("premiered", ""),
                'year': ret.get("year", ""),
                # 배우 이름은 이미 처리된 리스트에서 첫 번째 사용
                'actor': actor_names_for_log[0] if actor_names_for_log else "",
                'tagline': ret.get("tagline", ""),
            }
            ret["title"] = title_format.format(**format_dict)

        except KeyError as e:
            logger.error(f"타이틀 포맷팅 오류: 키 '{e}' 없음. 포맷: '{title_format}', 데이터: {format_dict}")
            ret["title"] = original_calculated_title # 오류 시 포맷팅 전 제목으로 복구
        except Exception as e_fmt:
            logger.exception(f"타이틀 포맷팅 중 예외 발생: {e_fmt}")
            ret["title"] = original_calculated_title # 오류 시 포맷팅 전 제목으로 복구

        if "tag" in ret:
            tag_option = P.ModelSetting.get(f"{self.name}_tag_option")
            if tag_option == "not_using":
                ret["tag"] = []
            elif tag_option == "label":
                label = ret.get("originaltitle", "").split("-")[0] if ret.get("originaltitle") else None
                if label: ret["tag"] = [label]
                else: ret["tag"] = []
            elif tag_option == "site":
                tmp = []
                label = ret.get("originaltitle", "").split("-")[0] if ret.get("originaltitle") else None
                for _ in ret.get("tag", []):
                    if label is None or _ != label:
                        tmp.append(_)
                ret["tag"] = tmp
        
        return ret

    def info2(self, code, site, keyword, ps_url=None):
        SiteClass = self.site_map.get(site, None)
        if SiteClass is None:
            logger.warning(f"info2: site '{site}'에 해당하는 SiteClass를 찾을 수 없습니다.")
            return None

        sett = self.__info_settings(site, code, keyword)
        sett['url_prefix_segment'] = 'jav/cen'

        logger.debug(f"info2: 사이트 '{site}'에서 코드 '{code}' 정보 조회 시작...")
        data = None
        try:
            # TODO
            if SiteClass in [SiteDmm, SiteJav321]:#SiteDmm]:
                data = SiteClass.info(code) 
            else:    
                data = SiteClass.info(code, **sett)
            
        except Exception as e_info:
            logger.exception(f"info2: 사이트 '{site}'에서 코드 '{code}' 정보 조회 중 오류 발생: {e_info}")
            return None

        if data and data.get("ret") == "success" and data.get("data"):
            ret = data["data"]
            logger.debug(f"info2: 사이트 '{site}'에서 코드 '{code}' 정보 조회 성공.")

            return ret
        else:
            response_ret = data.get('ret') if data else 'No response'
            has_data_field = bool(data.get('data')) if data and data.get('ret') == 'success' else False
            logger.warning(f"info2: 사이트 '{site}'에서 코드 '{code}' 정보 조회 실패. Response ret='{response_ret}', Has data field='{has_data_field}'")
            return None


    # endregion INFO
    ################################################


    ################################################
    # region ACTOR

    def process_actor(self, entity_actor):
        actor_site_list = P.ModelSetting.get_list(f"{self.name}_actor_order", ",")
        for site in actor_site_list:
            is_avdbs = site == 'avdbs'
            if self.process_actor2(entity_actor, site, is_avdbs=is_avdbs):
                return
        if not entity_actor.get("name", None):
            if entity_actor.get("originalname"):
                entity_actor["name"] = entity_actor.get("originalname")




    def process_actor2(self, entity_actor, site, is_avdbs=False) -> bool:
        originalname = entity_actor.get("originalname")
        if not originalname: 
            logger.warning("process_actor2: originalname이 없어 배우 정보를 처리할 수 없습니다.")
            return False

        SiteClass = self.site_map.get(site, None)
        if SiteClass is None:
            logger.warning(f"process_actor2: site '{site}'에 해당하는 SiteClass를 찾을 수 없습니다.")
            return False

        get_info_success = False
        try:
            if SiteClass in [SiteAvdbs]:
                get_info_success = SiteClass.get_actor_info(entity_actor)
            else:
                # hentaku 동작하지 않음.
                pass
                #get_info_success = SiteClass.get_actor_info(entity_actor, **sett)
        except Exception as e_getinfo:
            logger.exception(f"process_actor2: 사이트 '{site}'에서 배우 '{originalname}' 정보 조회 중 오류 발생: {e_getinfo}")
            get_info_success = False

        if get_info_success:
            updated_name = entity_actor.get("name", None)
            updated_thumb = entity_actor.get("thumb", None)
            logger.info(f"process_actor2: 사이트 '{site}'에서 '{originalname}' 정보 조회 성공. Name: {updated_name}, Thumb: {bool(updated_thumb)}")
            return True
        else:
            # logger.debug(f"process_actor2: 사이트 '{site}'에서 '{originalname}' 정보 조회 실패 또는 정보 없음.")
            return False


    # endregion ACTOR
    ################################################


    def __site_settings(self, site: str):
        db_prefix = f"{self.name}_{site}"
        proxy_url = None
        if P.ModelSetting.get_bool(f"{db_prefix}_use_proxy"):
            proxy_url = P.ModelSetting.get(f"{db_prefix}_proxy_url")

        final_settings = {
            "proxy_url": proxy_url,
            "image_mode": P.ModelSetting.get(f"{self.name}_image_mode"),
            "use_image_server": P.ModelSetting.get_bool(f"{self.name}_use_image_server"),
            "image_server_url": P.ModelSetting.get(f"{self.name}_image_server_url"),
            "image_server_local_path": P.ModelSetting.get(f"{self.name}_image_server_local_path"),
            "priority_label_setting_str": P.ModelSetting.get(f"{db_prefix}_priority_search_labels") 
        }

        if site in ['dmm', 'jav321']:
            final_settings["dmm_parser_rules"] = {
                "type0_rules": P.ModelSetting.get('jav_censored_dmm_parser_type0_rules'),
                "type1": P.ModelSetting.get('jav_censored_dmm_parser_type1_labels'),
                "type2": P.ModelSetting.get('jav_censored_dmm_parser_type2_labels'),
                "type3": P.ModelSetting.get('jav_censored_dmm_parser_type3_labels'),
                "type4": P.ModelSetting.get('jav_censored_dmm_parser_type4_labels'),
            }

        if site in ['mgstage', 'jav321', 'javbus', 'javdb']:
            setting_key = f"{db_prefix}_maintain_series_number_labels"
            final_settings["maintain_series_number_labels"] = P.ModelSetting.get(setting_key)

        # logger.debug(f"LOGIC: __site_settings for '{site}' prepared. Contains 'dmm_parser_rules': {'dmm_parser_rules' in final_settings}")
        # if 'dmm_parser_rules' in final_settings:
            # logger.debug(f"LOGIC: Content of dmm_parser_rules: {final_settings['dmm_parser_rules']}")

        # logger.debug(f"  Returning final settings for '{site}': proxy_url='{final_settings['proxy_url']}', priority_label='{final_settings['priority_label_setting_str']}'")
        return final_settings


    def __info_settings(self, site: str, code: str, keyword, ps_url=None):
        sett = self.__site_settings(site)
        
        db_prefix_info = f"{self.name}_{site}"

        sett["max_arts"] = P.ModelSetting.get_int(f"jav_censored_art_count")
        sett["use_extras"] = P.ModelSetting.get_bool(f"jav_censored_use_extras")
        
        sett["ps_to_poster_labels_str"] = P.ModelSetting.get(f"{db_prefix_info}_small_image_to_poster")
        sett["crop_mode_settings_str"] = P.ModelSetting.get(f"{db_prefix_info}_crop_mode")

        if keyword:
            sett["original_keyword"] = keyword

        # logger.debug(f"LOGIC: __info_settings for '{site}' inherits settings. Contains 'dmm_parser_rules': {'dmm_parser_rules' in sett}")
        # if 'dmm_parser_rules' in sett:
        #     logger.debug(f"LOGIC: Content of dmm_parser_rules in info_settings: {sett['dmm_parser_rules']}")

        # logger.debug(f"__info_settings for site '{site}', code '{code}': Prepared settings for SiteClass.info: {sett}")
        return sett



@app.route('/images')
@app.route('/images/<path:filename>')
def metadata_images(filename='index.html'):
    dist_path = os.path.join(F.path_data, 'images')
    file_path = os.path.join(dist_path, filename)
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        return send_from_directory(dist_path, 'index.html')
    return send_from_directory(dist_path, filename)

