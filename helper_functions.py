from CP_agents import CP_Daycare, CP_Child, CP_Family


def get_agent(agent_id, agents):
    """
    return a CP_agent instance for given id (including child / daycare / families)
    """
    agent = next((x for x in agents if x.id == agent_id), None)
    return agent


def create_children(children_dic):
    """
    create a list of CP_child instances from data stored in children_dic
    """
    children = []
    for c_id in children_dic.keys():
        c_id = children_dic[c_id]["id"]
        age = children_dic[c_id]["age"]
        if children_dic[c_id]["family_id"] is None:
            family_id = children_dic[c_id]["id"]
        else:
            family_id = children_dic[c_id]["family_id"]
        initial_daycare_id = (
            9999
            if children_dic[c_id]["initial_daycare_id"] is None
            else children_dic[c_id]["initial_daycare_id"]
        )
        actual_daycare_id = (
            9999
            if children_dic[c_id]["actual_daycare_id"] is None
            else children_dic[c_id]["actual_daycare_id"]
        )
        preference_list = children_dic[c_id]["preference_list"]
        # create a CP_Child instance
        c = CP_Child(
            c_id, age, family_id, initial_daycare_id, actual_daycare_id, preference_list
        )
        children.append(c)
    return children


def create_daycares(daycares_dic):
    """
    create a list of CP_Daycare instances from data stored in daycares_dic
    """
    daycares = []
    for d_id in daycares_dic.keys():
        d_id = daycares_dic[d_id]["id"]
        recruiting_numbers_list = daycares_dic[d_id]["recruiting_numbers_list"]
        share_ages_list = daycares_dic[d_id]["share_ages_list"]
        priority_child_id_list = daycares_dic[d_id]["priority_child_id_list"]
        priority_score_list = daycares_dic[d_id]["priority_score_list"]
        # create a CP_Daycare instance
        d = CP_Daycare(
            d_id,
            recruiting_numbers_list,
            share_ages_list,
            priority_child_id_list,
            priority_score_list,
        )
        daycares.append(d)
    # create a dummy daycare for being unmatched
    dummy_id = 9999
    recruiting_numbers_list = [9999 for i in range(6)]
    share_ages_list = []
    priority_child_id_list = []
    priority_score_list = []
    dummy = CP_Daycare(
        dummy_id,
        recruiting_numbers_list,
        share_ages_list,
        priority_child_id_list,
        priority_score_list,
    )
    daycares.append(dummy)
    return daycares


def create_families(families_dic):
    """
    create a list of CP_family instances from data stored in families_dic
    """
    families = []
    for f_id in families_dic.keys():
        f_id = families_dic[f_id]["id"]
        children_id_list = families_dic[f_id]["children"]
        pref_list = families_dic[f_id]["pref"]
        assignment = None
        # create a CP_Family instance
        f = CP_Family(f_id, children_id_list, pref_list, assignment)
        families.append(f)
    return families


def update_families_attributes(families):
    """
    for families with an only child,
        1) convert f.pref: list[int] into f.pref list[tuple(int)]
        2) convert None into 9999
    """
    for f in families:
        if f.has_siblings is False:
            f.pref = [tuple([d_id]) for d_id in f.pref]
        for pos in range(len(f.pref)):
            new = []
            tup_p = f.pref[pos]
            for item in tup_p:
                if item is None:
                    new.append(9999)
                else:
                    new.append(item)
            f.pref[pos] = tuple(new)


def update_children_attributes(children, families):
    """
    1) c.projected_pref is induced from f.pref
    2) c.all_daycare_ids is calulated from c.projected_pref
    """
    # update c.projected_pref
    for f in families:
        for pos in range(len(f.pref)):
            tup_p = f.pref[pos]
            for index, d_id in enumerate(tup_p):
                f_c = get_agent(f.children[index], children)
                f_c.projected_pref.append(tup_p[index])
    # update c.all_daycare_ids
    for c in children:
        c_d_ids = []
        for d_id in c.projected_pref:
            if d_id not in c_d_ids:
                c_d_ids.append(d_id)
        c.all_daycare_ids = c_d_ids


def update_daycares_attributes(children, daycares):
    """
    1) update the priority ordering / score list of dummy daycare 9999
    2) update d.priority_age_dic & d.priority_age_share_dic
    3）update d.total_numbers & d.total_numbers_share
    """
    # update dummy.priority
    dummy = get_agent(9999, daycares)
    for c in children:
        if 9999 in c.projected_pref and c.id not in dummy.priority:
            dummy.priority.append(c.id)

    # update dummy.score_list
    dummy.score_list = [100 for x in range(len(dummy.priority))]

    # update d.priority_age_dic & d.priority_age_share_dic & d.total_numbers
    for d in daycares:
        d.update_priority_age_dic(children)
        d.update_priority_age_share_dic(children)

    # update d.total_numbers
    for c in children:
        initial = get_agent(c.initial_daycare, daycares)
        initial.total_numbers[c.age] += 1

    # update d.total_numbers_share
    for d in daycares:
        d.total_numbers_share = d.total_numbers
        if len(d.all_shared_ages) > 0:
            for ages in d.share_ages_list:
                quota_ages = 0
                for age in ages:
                    quota_ages += d.total_numbers[age]
                for age in ages:
                    d.total_numbers_share[age] = quota_ages


def create_agents(children_dic, daycares_dic, families_dic):
    """
    Don't change the order of the following functions
    """
    children = create_children(children_dic)
    daycares = create_daycares(daycares_dic)
    families = create_families(families_dic)
    update_families_attributes(families)
    update_children_attributes(children, families)
    update_daycares_attributes(children, daycares)
    return children, daycares, families
